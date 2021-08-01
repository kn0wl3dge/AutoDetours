import docker
import os

from celery import shared_task
from django.utils import timezone

from workers.models import Worker
from jobs.models import JobState


NETWORK = "autodetours_autodetours_lan"
INPUT_DIR = os.environ.get("WIN7_IMAGES_DIR")
NB_WORKERS = int(os.environ.get("NB_WIN7_WORKERS"))
QEMU_IMAGE = "autodetours_qemu"


@shared_task
def worker_delete(ip):
    """Celery task used to remove a qemu container. This task
    is called whenever a worker has done its job to cleanup and
    restore its initial state.

    Args:
        ip (String): IP address of the container associated to the worker.
    """

    client = docker.DockerClient(base_url="unix://var/run/docker.sock")

    print("Looking up container using ip %s for deletion" % ip)
    for c in client.containers.list():
        for network, infos in c.attrs["NetworkSettings"]["Networks"].items():
            if infos["IPAddress"] == ip:
                print("Killing container %s" % c.name)
                c.kill()
                break


@shared_task
def workers_timeout():
    """Celery task to check if a worker has been running a job for too long.
    This mean that the job is taking too much time or simply that something
    crashed.
    """

    for worker in Worker.objects.filter(job__state=JobState.RUNNING):
        delta = timezone.now() - worker.job.start_time
        limit = worker.job.job_time * 5

        if delta.seconds > limit:
            print("Worker %s timed out !" % worker.id)
            worker.job.timeout()
            worker.job.save()
            worker_delete.delay(worker.ip)
            worker.delete()


@shared_task
def workers_automation():
    """Celery task to schedule worker creation and maintain the number
    of worker defined in the installation step.
    Its job is just to create container used to executes jobs.
    """

    client = docker.DockerClient(base_url="unix://var/run/docker.sock")

    cmd = [
        "-nographic",
        "-m 1024",
        "--enable-kvm",
        "-snapshot",
        '-incoming "exec: gzip -c -d /image/snapshot.gz"',
        "-hda /image/win7.qcow2",
    ]
    cmd = " ".join(cmd)

    for i in range(NB_WORKERS):
        worker = f"autodetours_workers_{i}"
        try:
            client.containers.get(worker)
        except docker.errors.NotFound:
            print(f"Runnning worker {worker}")
            client.containers.run(
                QEMU_IMAGE,
                command=cmd,
                network=NETWORK,
                devices=["/dev/kvm"],
                volumes={INPUT_DIR: {"bind": "/image", "mode": "ro"}},
                remove=True,
                name=worker,
                detach=True,
                privileged=True,
            )
