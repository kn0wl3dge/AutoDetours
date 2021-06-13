import json

from celery import shared_task

from tags import rule, extract
from jobs.models import Job

RULES_PATHS = ["tags/db_rules", "/data/db_rules"]

RULES = rule.get_db_rules(RULES_PATHS)


@shared_task
def set_tags(job):
    job = Job.objects.filter(pk=job).get()
    json_string = json.load(job.results)["results"]

    api_calls = extract.extract_funcname_list(json_string)
    tags = set()
    for rule in RULES:
        for pattern in rule.patterns:
            if pattern in api_calls:
                tags.add(rule.tag)

    job.extras_results["tags"] = list(tags)
    job.save()
