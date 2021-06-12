import uuid

from textwrap import wrap
from django.utils import timezone
from django.db import models
from django_fsm import FSMField, transition, RETURN_VALUE

from malwares.models import Malware, MalwareFormat

RESULTS_DIR = "/data/results"

def get_upload_filename(instance, filename):
    dirs = wrap(instance.malware.sha256, 2)
    ext = filename.split('.')[-1]
    return f"{RESULTS_DIR}/{'/'.join(dirs[:5])}/{instance.malware.sha256}_{instance.job_type}.{ext}"


class JobType(object):
    PESIEVE = 'PESieve'
    DETOURS = 'Detours'


class JobState(object):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    TIMED_OUT = "TIMED_OUT"


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    job_type = models.CharField(max_length=16)
    job_time = models.IntegerField(default=30)

    state = FSMField(default=JobState.NOT_STARTED, editable=False, protected=True)
    malware = models.ForeignKey(Malware, on_delete=models.CASCADE)

    results = models.FileField(upload_to=get_upload_filename, editable=False)
    extras_results = models.JSONField(default=dict, editable=False)

    creation_time = models.DateTimeField(auto_now_add=True, editable=False)
    start_time = models.DateTimeField(default=None, null=True, editable=False)
    end_time = models.DateTimeField(default=None, null=True, editable=False)

    @transition(
        field=state,
        source=JobState.NOT_STARTED,
        target=JobState.RUNNING,
    )
    def start(self):
        self.start_time = timezone.now()

    @transition(
        field=state,
        source=JobState.RUNNING,
        target=JobState.DONE,
    )
    def end(self, agent_results):
        self.end_time = timezone.now()
        self.results = agent_results
