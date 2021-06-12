import uuid

from textwrap import wrap
from django.utils import timezone
from django.db import models
from django_fsm import FSMField, transition, RETURN_VALUE

from malwares.models import Malware, MalwareFormat, MalwareState

RESULTS_DIR = "/data/results"

def get_upload_filename(instance, filename):
    dirs = wrap(instance.malware.sha256, 2)
    ext = filename.split('.')[-1]
    return f"{RESULTS_DIR}/{'/'.join(dirs[:5])}/{instance.malware.sha256}_{instance.job_type}.{ext}"


class JobType(object):
    PESIEVE = 'PESieve'
    DETOURS = 'Detours'


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    job_type = models.CharField(max_length=16)
    job_time = models.IntegerField(default=30)

    state = FSMField(default=MalwareState.NOT_STARTED, editable=False, protected=True)
    malware = models.ForeignKey(Malware, on_delete=models.CASCADE)

    results = models.FileField(upload_to=get_upload_filename, editable=False)
    extras_results = models.JSONField(default=dict, editable=False)

    date_start = models.DateTimeField(auto_now_add=True, editable=False)
    date_end = models.DateTimeField(default=None, null=True, editable=False)

    @transition(
        field=state,
        source=MalwareState.NOT_STARTED,
        target=MalwareState.RUNNING,
    )
    def job_start(self):
        pass

    @transition(
        field=state,
        source=MalwareState.RUNNING,
        target=MalwareState.DONE,
    )
    def job_end(self, agent_results):
        self.date_end = timezone.now()
        self.results = agent_results
