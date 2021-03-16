from celery import shared_task
import tags.rule as rule
import tags.extract as extract
from malwaredb.models import Malware

rules = rule.get_db_rules('tags/db_rules')


@shared_task
def set_tags(mal_sha256):
    malware = Malware.objects.filter(sha256=mal_sha256).get()
    json_string = malware.hooks_result
    api_calls = extract.extract_funcname_list(json_string)
    tags = []
    for rule in rules:
        for pattern in rule.patterns:
            if pattern in api_calls:
                tags.append(rule.tag)
                break
    malware.tags = tags
    malware.save()
