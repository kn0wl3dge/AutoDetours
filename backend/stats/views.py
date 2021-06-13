from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, F

from workers.models import Worker
from malwares.models import Malware
from jobs.models import Job, JobState, JobType


def get_state_repartition(qs, enum):
    return [
        qs.filter(state=v).count()
        for v, m in vars(enum).items()
        if not (v.startswith("_") or callable(m))
    ]


def get_worker_repartition():
    c = Worker.objects.count()
    c2 = Worker.objects.filter(job=None).count()
    return [c2, c - c2]


def get_timeline_chart(model, field):
    dates = (
        model.objects.datetimes(field, "minute")
        .values("datetimefield")
        .annotate(count_by_date=Count("id"))
    )
    return [{"t": str(d["datetimefield"]), "y": d["count_by_date"]} for d in dates]


def get_tags_area_repartition():
    results = Job.objects.filter(job_type=JobType.DETOURS).values("extras_results")
    tags = {}
    for result in results:
        if "tags" in result["extras_results"].keys():
            res_tags = result["extras_results"]["tags"]
            for tag in res_tags:
                if tag in tags.keys():
                    tags[tag] += 1
                else:
                    tags[tag] = 1

    tags = sorted(tags.items(), key=lambda x: x[1])[::-1]
    if len(tags) > 10:
        tags = tags[:10]
    return {"labels": [x[0] for x in tags], "count": [x[1] for x in tags]}


class StatsView(APIView):
    def get(self, request, pk=None):
        all_data = {
            "count": {
                "total_malwares": Malware.objects.count(),
                "total_jobs": Job.objects.count(),
                "total_jobs_done": Job.objects.filter(state=JobState.DONE).count(),
                "distinct_labels_number": Malware.objects.distinct("label").count(),
                "workers_number": Worker.objects.count(),
            },
            "jobs_repartition": get_state_repartition(Job.objects.all(), JobState),
            "workers_repartition": get_worker_repartition(),
            "jobs_timeline": get_timeline_chart(Job, "end_time"),
            "tags_area_repartition": get_tags_area_repartition(),
        }
        return Response(all_data)
