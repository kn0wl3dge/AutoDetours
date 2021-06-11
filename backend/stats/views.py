from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from django.db.models import Count

from workers.models import Worker, WorkerState
from malwares.models import Malware, MalwareState


def getStateRepartition(model, enum):
    return [
        model.objects.filter(state=v).count()
        for v, m in vars(enum).items()
        if not (v.startswith("_") or callable(m))
    ]


def getTimeLineChart(model, field):
    dates = (
        model.objects.datetimes(field, "minute")
        .values("datetimefield")
        .annotate(count_by_date=Count("name"))
    )
    return [{"t": str(d["datetimefield"]), "y": d["count_by_date"]} for d in dates]


def getMalwaresFamily():
    res = (
        Malware.objects.values("family")
        .annotate(nbr=Count("sha256"))
        .order_by("-nbr")
        .values("family", "nbr")
    )
    return {"labels": [x["family"] for x in res], "count": [x["nbr"] for x in res]}


class StatsView(APIView):
    def get(self, request, pk=None):
        all_data = {
            "count": {
                "total_malwares": Malware.objects.count(),
                "total_malwares_analyzed": Malware.objects.filter(
                    state=MalwareState.DONE
                ).count(),
                "distinct_labels_number": Malware.objects.distinct("label").count(),
                "workers_number": Worker.objects.count(),
            },
            "malwares_repartition": getStateRepartition(Malware, MalwareState),
            "workers_repartition": getStateRepartition(Worker, WorkerState),
            "malwares_analysis_timeline": getTimeLineChart(
                Malware, "analysis_ended_at"
            ),
            "malwares_family": getMalwaresFamily(),
        }
        return Response(all_data)
