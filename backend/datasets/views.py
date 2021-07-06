from os import remove
from django.http import FileResponse
from rest_framework import viewsets, mixins, throttling
from rest_framework.exceptions import Throttled
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from datasets.tasks import generate_dataset
from datasets.models import Dataset, DatasetStatus
from datasets.serializers import DatasetSerializer
from utils.renderers import PassRenderer

from jobs.models import Job, JobState


class DatasetRateThrottle(throttling.BaseThrottle):
    """The goal of this throttle is to avoid DoS using
    dataset feature.
    This throttle won't allow multiples dataset being
    generated simultaneously.
    """

    def allow_request(self, request, view):
        """This hook is called when a request is made to the viewset.

        Args:
            request (): Request made by the user.
            view (): View associated to the request.

        Returns:
            Bool: True if the request is allowed.
        """
        if view.action == "create":
            q = Dataset.objects.filter(status=DatasetStatus.GENERATING)
            return not q.exists()
        return True


class DatasetViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet used to render Dataset objects to user.
    It does not allow modification of existing objects.
    """

    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    throttle_classes = (DatasetRateThrottle,)

    def throttled(self, request, wait):
        """Custom error returned when the request isn't allowed.

        Args:
            request (Request): Request made by the user.
            view (View): View associated to the request.

        Raises:
            Throttled: A dataset is already being generated...
        """
        raise Throttled(
            detail={
                "error": "A dataset is already being generated...",
            }
        )

    def perform_create(self, serializer):
        """Hook Dataset creation to call a celery task used to generate
        the zipfile. Only generate a Dataset if there is results.

        Args:
            serializer (Serializer): Serializer used to create the object
                from user input.
        Raises:
            ValidationError: Can't generate an empty dataset.
        """
        if Job.objects.filter(state=JobState.DONE).exists():
            dataset = serializer.save()
            generate_dataset.delay(dataset.pk)
        else:
            raise ValidationError(
                "Can't generate an empty dataset. You need finished jobs to do that."
            )

    def perform_destroy(self, instance):
        """Hook Dataset deletion to verify that the dataset has been generated
        and remove the associated zipfile.

        Args:
            instance (Dataset): Dataset object being deleted.

        Raises:
            ValidationError: Dataset generation is not finished yet.
        """
        if instance.status == DatasetStatus.GENERATING:
            raise ValidationError("Dataset generation isn't finished yet.")

        zip_path = instance.file
        super().perform_destroy(instance)

        try:
            remove(zip_path)
        except OSError as e:
            pass

    @action(detail=True, methods=["get"], renderer_classes=(PassRenderer,))
    def download(self, request, pk=None):
        """Extra endpoint to download the zipfile associated to a Dataset.

        Args:
            request (request): Request made by user.
            pk (Integer, optional): Primary key of the Dataset.
                Defaults to None.

        Returns:
            FileResponse: Reponse containing the dataset zipfile.
        """
        dataset = get_object_or_404(Dataset, pk=pk)

        file_handle = open(dataset.file, "rb")

        response = FileResponse(file_handle, content_type="application/zip")
        response["Content-Disposition"] = (
            'attachment; filename="dataset_%s"' % dataset.file.split("/")[-1]
        )

        return response
