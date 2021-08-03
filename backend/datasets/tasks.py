import zipfile

from os import path as ospath, walk
from django.utils import timezone, dateformat
from celery import shared_task

from jobs.models import RESULTS_DIR
from datasets.models import Dataset, DatasetStatus, DATASET_DIR


def zipdir(path, ziph):
    """Add every files stored in directories and subdirectories in a zipfile

    Args:
        path (String): Path to the directory being ziped
        ziph (ZipFile): ZipFile object representing the zipfile
    """
    for root, dirs, files in walk(path):
        for file in files:
            ziph.write(
                ospath.join(root, file),
                ospath.relpath(ospath.join(root, file), ospath.join(path, "..")),
            )


@shared_task
def generate_dataset(dataset):
    """Celery task to create a zipfile that contains jobs results

    Args:
        dataset (Integer): Primary Key (id) of a Dataset object in database
    """
    zip_path = f"{DATASET_DIR}/{dateformat.format(timezone.now(), 'Y-m-d_H-i-s')}.zip"
    zipf = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    zipdir("/data/" + RESULTS_DIR, zipf) # TODO :  Use django media root
    zipf.close()

    dataset = Dataset.objects.filter(pk=dataset).get()
    dataset.file = zip_path
    dataset.status = DatasetStatus.GENERATED
    dataset.save()
