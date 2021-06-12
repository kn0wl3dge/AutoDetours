from os import remove
from json import dumps
from django.http import FileResponse
from rest_framework import viewsets, mixins, throttling
from rest_framework.exceptions import Throttled
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from datasets.tasks import generate_dataset
from datasets.models import Dataset, DatasetStatus
from datasets.serializers import DatasetSerializer
from utils.renderers import PassRenderer


class DatasetRateThrottle(throttling.BaseThrottle):
    """
    The goal of this throttle is to avoid DoS using 
    dataset feature.
    This throttle won't allow multiples dataset being
    generated simultaneously.
    """
    def allow_request(self, request, view):
        if view.action == 'create':
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
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    throttle_classes = (DatasetRateThrottle,)

    def throttled(self, request, wait):
        raise Throttled(
            detail={
                "error":"A dataset is already being generated...",
            }
        )


    def perform_create(self, serializer):
        dataset = serializer.save()
        generate_dataset.delay(dataset.pk)
    
    def perform_destroy(self, instance):
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
        dataset = get_object_or_404(Dataset, pk=pk)

        file_handle = open(dataset.file, 'rb')

        response = FileResponse(file_handle, content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="dataset_%s"' % dataset.file.split('/')[-1]

        return response