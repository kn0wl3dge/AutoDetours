from os import fstat
from json import dumps
from django.http import FileResponse
from rest_framework import viewsets, mixins, renderers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from datasets.tasks import generate_dataset

class DatasetGenerationView(APIView):
    def get(self, request, pk=None):
        task_id = generate_dataset.delay()
        return Response({"task_id": task_id.__str__()})


class DatasetCheckView(APIView):
    def get(self, request, pk=None):
        if pk is None:
            return Response({"status": "KO", "error": "Please specify a task id."})
        path = "/data/datasets/" + pk + ".zip"
        try:
            fd = open(path, "rb")
        except:
            return Response(
                {
                    "status": "KO",
                    "error": "Dataset does not exist or is not yet generated.",
                }
            )
        return Response({"status": "OK"})


class DatasetDownloadView(APIView):
    def get(self, request, pk=None):
        if pk is None:
            return Response({"error": "Please specify a task id."})
        path = "/data/datasets/" + pk + ".zip"
        try:
            fd = open(path, "rb")
        except:
            return Response(
                {"error": "Dataset does not exist or is not yet generated."}
            )

        response = FileResponse(fd, content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="dataset.zip"'

        return response
