from rest_framework import mixins, viewsets, status
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
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

    def perform_destroy(self, instance):
        if instance.job and instance.job.state != JobState.DONE:
            raise ValidationError("You can't delete a worker in this state")
        ip = instance.ip
        instance.delete()
        worker_delete.delay(ip)

    @action(detail=True, methods=["GET"])
    def get_task(self, request, pk=None):
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
