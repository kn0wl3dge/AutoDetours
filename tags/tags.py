from celery import Celery
import rule

BROKER_URL = 'redis://localhost:6379/0'

celery_app = Celery('Restaurant', broker=BROKER_URL)

rules = rule.get_db_rules('db_rules')


@celery_app.task
def set_tags(api_calls):
    tags = []
    for rule in rules:
        for pattern in rule.patterns:
            if pattern in api_calls:
                tags.append(rule.tag)
                break
    return tags