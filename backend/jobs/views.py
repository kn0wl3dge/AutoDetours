from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from jobs.serializers import JobSerializer
from jobs.models import Job
from utils.renderers import PassRenderer


class JobViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet used to render Job objects to user.
    It does not allow modification of existing objects.
    """

    queryset = Job.objects.all()
    serializer_class = JobSerializer

    @action(detail=True, methods=["GET"], renderer_classes=(PassRenderer,))
    def download_results(self, request, pk=None):
        """Extra endpoint to download the results associated to a Job.

        Args:
            request (request): Request made by user.
            pk (UUID, optional): Primary key of the Job.
                Defaults to None.

        Returns:
            FileResponse: Reponse containing the job results.
        """
        job = get_object_or_404(Job, pk=pk)

        output = job.results
        extension = output.path.split(".")[-1]

        response = FileResponse(output, content_type="application/" + extension)
        response["Content-Length"] = len(output)
        response["Content-Disposition"] = 'attachment; filename="%s.%s"' % (
            job.malware.sha256,
            extension,
        )
        return response
