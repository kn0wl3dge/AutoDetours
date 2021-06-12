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
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
            )

@shared_task
def generate_dataset(dataset):
    zip_path = f"{DATASET_DIR}/{dateformat.format(timezone.now(), 'Y-m-d_H-i-s')}.zip"
    zipf = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    zipdir(RESULTS_DIR, zipf)
    zipf.close()

    dataset = Dataset.objects.filter(pk=dataset).get()
    dataset.file = zip_path
    dataset.status = DatasetStatus.GENERATED
    dataset.save()
