import uuid

from django.db import models
from django_fsm import FSMField, transition

from malwares.models import Malware, MalwareState


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

    @transition(field=state, source=WorkerState.REGISTERED, target=WorkerState.TASKED)
    def find_task(self):
        available_jobs = Job.objects.filter(state=MalwareState.NOT_STARTED)
        if available_jobs.exists():
            job = available_jobs.earliest("start_time")
            job.start()
            job.save()
            self.job = job
        else:
            raise NoTaskAvailable

    @transition(field=state, source=WorkerState.TASKED, target=WorkerState.FINISHED)
    def end_task(self, report):
        self.job.end(report)
        self.job.save()
