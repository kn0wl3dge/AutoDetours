import docker
import os

from celery import shared_task
from django.utils import timezone

from workers.models import Worker, WorkerState


@shared_task
def worker_delete(ip):
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
    # TODO FIX ME
    for worker in Worker.objects.filter(state=WorkerState.TASKED):
        delta = timezone.now() - worker.analysis_start_date
        limit = worker.malware.time * 20
        if limit > 3 * 10 * 60:  # 30minutes max of timeout after analysis
            limit = 3 * 10 * 60
        if delta.seconds > limit:
            print("Worker %s timed out !" % worker.id)
            worker.malware.end_analysis(None)
            worker.malware.save()
            worker_delete.delay(worker.ip)
            worker.delete()


@shared_task
def workers_automation():
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
