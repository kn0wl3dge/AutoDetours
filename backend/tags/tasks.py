import jsonlines

from celery import shared_task

from jobs.models import Job
from tags.rule import RULES_PATHS, get_rules, get_apicalls_from_traces


@shared_task
def set_tags(job):
    """Celery task to generates tags results from Detours traces
    and defined Rules.

    Args:
        job (UUID): Job UUID (primary key).
    """
    rules = get_rules(RULES_PATHS)

    job = Job.objects.filter(pk=job).get()
    with jsonlines.open(job.results.path) as jl_reader:
        api_calls = get_apicalls_from_traces(jl_reader)

    tags = set()
    for rule in rules:
        for pattern in rule.patterns:
            if pattern in api_calls:
                tags.add(rule.tag)

    job.extras_results["tags"] = list(tags)
    job.save()
