from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from workers.models import Worker
from workers.serializers import WorkerSerializer
from workers.tasks import worker_delete

from jobs.models import Job, JobType, JobState

from tags.tasks import set_tags


class WorkerViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet used to render Worker objects to user.
    It does not allow modification of existing objects.
    """

    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

    def perform_destroy(self, instance):
        """Hook worker object deletion to check that it is not currently
        executing a job.

        Args:
            instance (Worker): Worker object being destroyed.

        Raises:
            ValidationError: You can't delete a worker in this state.
        """
        if instance.job and instance.job.state != JobState.DONE:
            raise ValidationError("You can't delete a worker in this state")
        ip = instance.ip
        instance.delete()
        worker_delete.delay(ip)

    @action(detail=True, methods=["GET"])
    def get_task(self, request, pk=None):
        """Extra API endpoint being called by Windows Agent to find a
        job to do. Gives every needed information to the Agent and
        update objects states accordingly.

        Args:
            request (Request): Request made by the Agent.
            pk (UUID, optional): Worker UUID. Defaults to None.

        Returns:
            Response: Job configuration for the agent (malware hash,
                job execution time, binary format, DLL Export...)
        """
        worker = get_object_or_404(Worker, pk=pk)
        if not worker.job:
            available_jobs = Job.objects.filter(state=JobState.NOT_STARTED)
            if available_jobs.exists():
                job = available_jobs.earliest("creation_time")
                job.start()
                job.save()
                worker.job = job
                worker.save()

                return Response(
                    {
                        "malware": worker.job.malware.sha256,
                        "time": worker.job.job_time,
                        "task": worker.job.job_type,
                        "format": worker.job.malware.format,
                        "exportName": worker.job.malware.export_dll,
                    }
                )
            else:
                return Response({"error": "No task available"})
        else:
            return Response({"error": "Worker is already tasked"})

    @action(detail=True, methods=["POST"])
    def submit_task(self, request, pk=None):
        """Extra API endpoint used by the Windows Agent to submit results
        of its job. The results are send through a file (currently being
        a JSON or a ZIP)/

        Args:
            request (Request): Request made by the Agent.
            pk (UUID, optional): Worker UUID. Defaults to None.

        Returns:
            Response: Send back if results storing was a success or if any
                error has been encoutered.
        """
        worker = get_object_or_404(Worker, pk=pk)
        if worker.job and worker.job.state != JobState.DONE:
            if "results" in request.data.keys():
                worker.job.end(request.data["results"])
                worker.job.save()

                # Prevents JSON deserialization from zip file
                if worker.job.job_type == JobType.DETOURS:
                    set_tags.delay(worker.job.id)

                return Response({"success": "Results successfully stored"})
            else:
                return Response({"error": "Can't find 'results' param"})
        return Response({"error": "Worker is in an incorrect state"})
