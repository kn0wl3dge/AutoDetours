import docker

from celery import shared_task

@shared_task
def worker_delete(ip):
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    for c in client.containers.list():
        print(c.attrs['NetworkSettings']['IPAddress'])
        if c.attrs['NetworkSettings']['IPAddress'] == ip:
            print("Killing container %s" % c.name)
            c.kill()
            break

@shared_task
def workers_automation():
    input_dir = "D:/IE9.Win7.VirtualBox/"
    output_dir = "/image/"
    network = "autodetours_autodetours_lan"
    workers = {
        "autodetours_worker1": "win7.qcow2",
        "autodetours_worker2": "win7-1.qcow2",
        "autodetours_worker3": "win7-2.qcow2",
        "autodetours_worker4": "win7-3.qcow2",
        "autodetours_worker5": "win7-4.qcow2",
    }
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
