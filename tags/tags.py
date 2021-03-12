import extract
import rule
import extract
from celery import Celery

BROKER_URL = 'redis://localhost:6379/0'

celery_app = Celery('Restaurant', broker=BROKER_URL)

@celery_app.task
def set_tags(api_calls, rules):
    tags = []
    print(type(rules))
    for rule in rules:
        print(type(rule))
        for pattern in rule["patterns"]:
            if pattern in api_calls:
                tags.append(rule.tag)
                break
    print(tags)
