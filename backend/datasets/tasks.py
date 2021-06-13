import errno
import os
import zipfile

from shutil import rmtree
from celery import shared_task
from textwrap import wrap
from rest_framework.renderers import JSONRenderer
from django.utils import timezone, dateformat
from celery import shared_task

from malwares.models import Malware
from malwares.serializers import MalwareSerializer
from jobs.models import JobState, RESULTS_DIR
from datasets.models import Dataset, DatasetStatus, DATASET_DIR


def zipdir(path, ziph):
    """Add every files stored in directories and subdirectories in a zipfile

    Args:
        path (String): Path to the directory being ziped
        ziph (ZipFile): ZipFile object representing the zipfile
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
            )


@shared_task
def generate_dataset(dataset):
    """Celery task to create a zipfile that contains jobs results

    Args:
        dataset (Integer): Primary Key (id) of a Dataset object in database
    """
    zip_path = f"{DATASET_DIR}/{dateformat.format(timezone.now(), 'Y-m-d_H-i-s')}.zip"
    zipf = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    zipdir(RESULTS_DIR, zipf)
    zipf.close()

    dataset = Dataset.objects.filter(pk=dataset).get()
    dataset.file = zip_path
    dataset.status = DatasetStatus.GENERATED
    dataset.save()
