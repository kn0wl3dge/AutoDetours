import uuid

from django.db import models
from django_fsm import FSMField, transition

from malwaredb.models import Malware, MalwareState


class NoTaskAvailable(Exception):
    """No task are currently available"""
    pass


class WorkerState(object):
    REGISTERED = "REGISTERED"
    TASKED = "TASKED"
    FINISHED = "FINISHED"


class Worker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    malware = models.ForeignKey(Malware, on_delete=models.CASCADE, null=True,
                                editable=False)
    state = FSMField(default=WorkerState.REGISTERED, protected=True,
                     editable=False)
    date = models.DateTimeField(auto_now_add=True, editable=False)

    @transition(field=state, source=WorkerState.REGISTERED,
                target=WorkerState.TASKED)
    def find_task(self):
        potential_tasks = Malware.objects.filter(state=MalwareState.NOT_ANALYZED)
        if potential_tasks.exists():
            malware = potential_tasks.earliest("date")
            malware.analyze()
            malware.save()
            self.malware = malware
        else:
            raise NoTaskAvailable

    @transition(field=state, source=WorkerState.TASKED,
                target=WorkerState.FINISHED)
    def finish_task(self, report):
        self.malware.end_analysis(report)
        self.malware.save()
        # TODO : kill the VM
