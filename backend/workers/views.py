from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from workers.models import Worker, WorkerState
from workers.serializers import WorkerSerializer

from workers.tasks import worker_delete


class WorkerViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        worker_delete.s(request.headers['X-Forwarded-For']) # This is not safe !!!
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        if instance.state != WorkerState.FINISHED:
            raise ValidationError("You can delete a worker in this state")
        instance.delete()

    @action(detail=True, methods=['GET'])
    def get_task(self, request, pk=None):
        worker = get_object_or_404(Worker, pk=pk)
        if worker.state == WorkerState.REGISTERED:
            try:
                worker.find_task()
                worker.save()
            except:
                return Response({"error": "No task available"})
            return Response({"malware": worker.malware.sha256, "time": worker.malware.time})
        else:
            return Response({"error": "Worker is busy"})

    @action(detail=True, methods=['POST'])
    def submit_task(self, request, pk=None):
        worker = get_object_or_404(Worker, pk=pk)
        if worker.state == WorkerState.TASKED:
            if "results" in request.data.keys():
                try:
                    worker.finish_task(request.data["results"])
                    worker.save()
                except:
                    return Response({"error": "Results can't be parsed"})
                return Response({"success": "Results successfully stored"})
            else:
                return Response({"error": "Can't find 'results' param"})
        return Response({"error": "Worker is in an incorrect state"})
