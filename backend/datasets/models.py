from django.db import models


DATASET_DIR = "datasets"  # /data/datasets


class DatasetStatus(object):
    """This class is used to represent a state of a Dataset entry.

    GENERATING : Dataset zipfile is being generated.
    GENERATED : Dataset zipfile generation is done.
    """

    GENERATING = "GENERATING"
    GENERATED = "GENERATED"


class Dataset(models.Model):
    """This model represents a Dataset. A dataset is a zipfile containing all
    the jobs results organized in multiples directories depending on the hash
    of the sample.
    """

    # File
    file = models.FilePathField(DATASET_DIR, editable=False)

    # State
    status = models.CharField(
        default=DatasetStatus.GENERATING, max_length=32, editable=False
    )

    # Datetime
    creation_time = models.DateTimeField(auto_now_add=True, editable=False)
