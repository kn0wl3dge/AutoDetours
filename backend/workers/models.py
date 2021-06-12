import uuid

from django.db import models
from django_fsm import FSMField, transition

from malwares.models import Malware
from jobs.models import Job, JobState


class NoTaskAvailable(Exception):
    """No task are currently available"""

    pass


class WorkerState(object):
    REGISTERED = "REGISTERED"
    TASKED = "TASKED"
    FINISHED = "FINISHED"


class Worker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    ip = models.GenericIPAddressField(editable=False)

    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, null=True, editable=False
    )

    registration_time = models.DateTimeField(auto_now_add=True, editable=False)
