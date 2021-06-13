from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, F

from workers.models import Worker
from malwares.models import Malware
from jobs.models import Job, JobState


def getStateRepartition(qs, enum):
    return [
        qs.filter(state=v).count()
        for v, m in vars(enum).items()
        if not (v.startswith("_") or callable(m))
    ]


def getTimeLineChart(model, field):
    dates = (
        model.objects.datetimes(field, "minute")
        .values("datetimefield")
        .annotate(count_by_date=Count("id"))
    )
    return [{"t": str(d["datetimefield"]), "y": d["count_by_date"]} for d in dates]


class StatsView(APIView):
    def get(self, request, pk=None):
        all_data = {
            "count": {
                "total_malwares": Malware.objects.count(),
                "totoal_jobs": Job.objects.count(),
                "total_jobs_done": Job.objects.filter(
                    state=JobState.DONE
                ).count(),
                "distinct_labels_number": Malware.objects.distinct("label").count(),
                "workers_number": Worker.objects.count(),
            },
            "job_repartition": getStateRepartition(Job.objects.all(), JobState),
            "workers_repartition": getStateRepartition(Worker.objects.annotate(state=F("job__state")), JobState),
            "jobs_timeline": getTimeLineChart(
                Job, "end_time"
            )
        }
        return Response(all_data)
