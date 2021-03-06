from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from workers.models import Worker
from malwaredb.models import Malware


def get_malware_list():
    return Malware.objects.all()


def get_workers_list():
    return Worker.objects.all()


def get_info_state_malware():
    queryset = get_malware_list()
    data = [0, 0, 0]
    for malware in queryset:
        if malware.state == "ANALYZED":
            data[2] += 1
        elif malware.state == "ANALYZING":
            data[1] += 1
        if malware.state == "NOT_ANALYZED":
            data[0] += 1
    
    return data


class StatsView(APIView):
    def get(self, request, pk=None):
        toto = {
            'toto' : 'tata',
        }
        return Response(toto)