import docker

from celery import shared_task
from django.utils import timezone

from workers.models import Worker, WorkerState

@shared_task
def worker_delete(ip):
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    print("Looking up container using ip %s for deletion" % ip)
    for c in client.containers.list():
        for network, infos in c.attrs['NetworkSettings']['Networks'].items():
            if infos['IPAddress'] == ip:
                print("Killing container %s" % c.name)
                c.kill()
                break

@shared_task
def workers_timeout():
    for worker in Worker.objects.filter(state=WorkerState.TASKED):
        delta = timezone.now() - worker.analysis_start_date
        if delta.seconds > worker.malware.time * 3:
            print("Worker %s timed out !" % worker.id)
            worker.malware.end_analysis({"error": "Timed out.."})
            worker.malware.save()
            worker_delete.delay(worker.ip)
            worker.delete()

@shared_task
def workers_automation():
    input_dir = "/home/ssg/Documents/qemu_img/"
    output_dir = "/image/"
    network = "autodetours_autodetours_lan"
    nb_workers = 5 # Change Me
    workers = {}
    for i in range(nb_workers):
        workers["autodetours_workers_%i" %i] = "win7-%i.qcow2" % i
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    for worker, image in workers.items():
        try:
            client.containers.get(worker)
        except docker.errors.NotFound:
            print("Runnning worker %s" % worker)
            client.containers.run(
                "qemu",
                command=f"-hda {output_dir}{image}",
                network=network,
                volumes={input_dir: {'bind': output_dir, 'mode': 'rw'}},
                remove=True,
                name=worker,
                detach=True
            )
