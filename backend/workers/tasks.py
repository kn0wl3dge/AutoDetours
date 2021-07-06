import docker
import os

from celery import shared_task
from django.utils import timezone

from workers.models import Worker
from jobs.models import JobState


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
    input_dir = os.environ.get("WIN7_IMAGES_DIR")
    output_dir = "/image/"
    network = "autodetours_autodetours_lan"
    nb_workers = int(os.environ.get("NB_WIN7_WORKERS"))
    workers = {}
    for i in range(nb_workers):
        workers["autodetours_workers_%i" % i] = "win7-%i.qcow2" % i
    client = docker.DockerClient(base_url="unix://var/run/docker.sock")

    for worker, image in workers.items():
        try:
            client.containers.get(worker)
        except docker.errors.NotFound:
            print("Runnning worker %s" % worker)
            client.containers.run(
                "autodetours_qemu",
                command=f"-nographic -m 1024 -loadvm agent -enable-kvm -hda {output_dir}{image}",
                network=network,
                devices=["/dev/kvm"],
                volumes={input_dir: {"bind": output_dir, "mode": "rw"}},
                remove=True,
                name=worker,
                detach=True,
                privileged=True,
            )
