import uuid

from django.utils import timezone
from django.db import models
from django_fsm import FSMField, transition

from malware.models import Malware, MalwareState


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
    malware = models.ForeignKey(
        Malware, on_delete=models.CASCADE, null=True, editable=False
    )
    state = FSMField(default=WorkerState.REGISTERED, protected=True, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    analysis_start_date = models.DateTimeField(default=None, null=True, editable=False)
    analysis_end_date = models.DateTimeField(default=None, null=True, editable=False)

    @transition(field=state, source=WorkerState.REGISTERED, target=WorkerState.TASKED)
    def find_task(self):
        potential_tasks = Malware.objects.filter(state=MalwareState.NOT_STARTED)
        if potential_tasks.exists():
            malware = potential_tasks.earliest("creation_date")
            malware.starting_task()
            malware.save()
            self.malware = malware
            self.analysis_start_date = timezone.now()
        else:
            raise NoTaskAvailable

    @transition(field=state, source=WorkerState.TASKED, target=WorkerState.FINISHED)
    def finish_task(self, report):
        self.malware.end_analysis(report)
        self.malware.save()
        self.analysis_end_date = timezone.now()
