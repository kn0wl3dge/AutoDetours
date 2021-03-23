from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from os import walk

from workers.models import Worker, WorkerState
from workers.serializers import WorkerSerializer
from workers.tasks import worker_delete

from tags.tags import set_tags
from tags.rule import Rule

class WorkerViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                    mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

    def perform_destroy(self, instance):
        if instance.state != WorkerState.FINISHED:
            raise ValidationError("You can delete a worker in this state")
        ip = instance.ip
        instance.delete()
        worker_delete.delay(ip)

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
                    set_tags.delay(worker.malware.sha256)
                except:
                    return Response({"error": "Results can't be parsed"})
                return Response({"success": "Results successfully stored"})
            else:
                return Response({"error": "Can't find 'results' param"})
        return Response({"error": "Worker is in an incorrect state"})

class RuleFormView(APIView):
    def post(self, request):
        rule = request.data['rule']
        functions = request.data['functions']
        tag = request.data['tag']
        with open("tags/db_rules/" + rule.lower() + ".yml", "w") as f:
            f.write("name: %s\n" % rule)
            f.write("features:\n")
            for func in functions:
                f.write("   - %s\n" % func)
            f.write("tag: %s" % tag)
        return Response({"success": "OK"})

    def get(self, request):
        rules_list = []
        for files in walk("tags/db_rules"):
            f = (files, 'r')
            content = f.readlines()
            rules_list.append()
        return Response(list)
