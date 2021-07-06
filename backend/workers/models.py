import uuid

from django.db import models

from malwares.models import Malware
from jobs.models import Job


class Worker(models.Model):
    """This model represents a Worker. Each worker is associated with
    a windows VM running in QEMU. Workers are executing jobs associated
    to malwares.
    """

    # ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    ip = models.GenericIPAddressField(editable=False)

    # Job
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, editable=False)

    # Datetime
    registration_time = models.DateTimeField(auto_now_add=True, editable=False)
