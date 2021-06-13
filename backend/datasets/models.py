from django.db import models


DATASET_DIR = "/data/datasets"


class DatasetStatus(object):
    GENERATING = "Generating"
    GENERATED = "Generated"


class Dataset(models.Model):
    file = models.FilePathField(DATASET_DIR, editable=False)
    status = models.CharField(
        default=DatasetStatus.GENERATING, max_length=32, editable=False
    )
    creation_time = models.DateTimeField(auto_now_add=True, editable=False)
