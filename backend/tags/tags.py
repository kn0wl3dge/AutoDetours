from celery import shared_task
import tags.rule as rule
import tags.extract as extract

rules = rule.get_db_rules('tags/db_rules')


@shared_task
def set_tags(json_string):
    json_content = extract.convert_to_json(json_string)
    api_calls = extract.extract_funcname_list(json_content)

    tags = []
    for rule in rules:
        for pattern in rule.patterns:
            if pattern in api_calls:
                tags.append(rule.tag)
                break
    return tags
