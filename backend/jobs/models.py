import uuid

from textwrap import wrap
from django.utils import timezone
from django.db import models
from django_fsm import FSMField, transition

from malwares.models import Malware

RESULTS_DIR = "results"  # /data/results


def get_upload_filename(instance, filename):
    """Compute path where the job result will be stored.

    Args:
        instance (Job): Job instance associated to the results.
        filename (String): Name of the uploaded file.

    Returns:
        String: Computed path where the results will be stored.
    """
    dirs = wrap(instance.malware.sha256, 2)
    ext = filename.split(".")[-1]
    return f"{RESULTS_DIR}/{'/'.join(dirs[:5])}/{instance.malware.sha256}_{instance.job_type}.{ext}"


class JobType(
    object
):  # TODO change this in the agent and make a validation in the view (job creation)
    """List all possibles jobs that can be passed to an agent.

    PESIEVE : Tool used to unpack PE malwares.
    DETOURS : Microsoft tool used to hook windows system calls.
    """

    PESIEVE = "PESieve"
    DETOURS = "Detours"


class JobState(object):
    """List all possibles states of a Job.

    NOT_STARTED : Job is scheduled but not associated to any worker.
    RUNNING : Job is currently being executed by a worker.
    DONE : Job is done and results are stored in the backend.
    TIMED_OUT : Job could not finish in time or just crashed.
    """

    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    TIMED_OUT = "TIMED_OUT"


class Job(models.Model):
    """This model represents a Job. Jobs are used to analyze a malware.
    They are sended to windows workers represented by the Worker model.

    extra_results can be used afterwards to store new results based
    on computation on the results file.
    """

    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Config
    job_type = models.CharField(max_length=16)
    job_time = models.IntegerField(default=30)

    # State
    state = FSMField(default=JobState.NOT_STARTED, editable=False, protected=True)
    malware = models.ForeignKey(Malware, related_name="jobs", on_delete=models.CASCADE)

    # Results
    results = models.FileField(upload_to=get_upload_filename, editable=False)
    extras_results = models.JSONField(default=dict, editable=False)

    # Datetimes
    creation_time = models.DateTimeField(auto_now_add=True, editable=False)
    start_time = models.DateTimeField(default=None, null=True, editable=False)
    end_time = models.DateTimeField(default=None, null=True, editable=False)

    @transition(
        field=state,
        source=JobState.NOT_STARTED,
        target=JobState.RUNNING,
    )
    def start(self):
        """Called when a job is started to update Job state."""

        self.start_time = timezone.now()

    @transition(
        field=state,
        source=JobState.RUNNING,
        target=JobState.DONE,
    )
    def end(self, agent_results):
        """Called when a job is finished to update its state
        and store the associated results.

        Args:
            agent_results (): File that contains the results.
        """
        self.end_time = timezone.now()
        self.results = agent_results

    @transition(
        field=state,
        source=JobState.RUNNING,
        target=JobState.TIMED_OUT,
    )
    def timeout(self):
        """Called when a job timed out."""
        self.end_time = timezone.now()
