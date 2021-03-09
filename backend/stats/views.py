from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from workers.models import Worker
from malwaredb.models import Malware


def get_malwares_list():
    return Malware.objects.all()


def get_workers_list():
    return Worker.objects.all()


def get_info_state_malwares():
    queryset = get_malwares_list()
    data = [0, 0, 0]
    for malware in queryset:
        if malware.state == "ANALYZED":
            data[2] += 1
        elif malware.state == "ANALYZING":
            data[1] += 1
        if malware.state == "NOT_ANALYZED":
            data[0] += 1
    
    return data


def get_info_workers():
    queryset = get_workers_list()
    data = [0, 0, 0]
    for worker in queryset:
        if worker.state == "REGISTERED":
            data[2] += 1
        if worker.state == "TASKED":
            data[1] += 1
        if worker.state == "FINISHED":
            data[0] += 1
    
    return data


class StatsView(APIView):
    def get(self, request, pk=None):
        data = get_info_state_malwares()
        status_worker = get_info_workers()
        all_data = { 
            'datafrommalware': {
                'status' : data,
            },
            'infoworkers': {
                'status' : status_worker
            }
        }
        return Response(all_data)
