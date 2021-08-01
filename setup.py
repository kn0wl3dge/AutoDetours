import argparse
import docker
import json
import logging
import os
import paramiko
import secrets
import socket
import sys
import tarfile
import wget
import zipfile

from scp import SCPClient
from shutil import copyfile, rmtree
from subprocess import Popen, PIPE
from time import sleep

# Constants
DEV = False
HOST = "127.0.0.1"
SSH_PORT = 2222
QMP_PORT = 2223
DOCKER_SOCKET = "unix://var/run/docker.sock"
WORKERS_DIR = os.path.dirname(os.path.realpath(__file__)) + "/workers"
BASE_QCOW2 = WORKERS_DIR + "/base.qcow2"
WORKER_QCOW2 = "win7.qcow2"
WORKER_SNAPSHOT = "snapshot.gz"
INSTALL_CONTAINER = "autodetours_qemu_gen"
ENV_FILE = ".env"
SSH_USERNAME = "IEUser"
SSH_PASSWORD = "Passw0rd!"
WINDOWS_PATH = "/cygdrive/c/Temp"
QEMU_IMAGE = "autodetours_qemu"
WIN7_URL = "https://az792536.vo.msecnd.net/vms/VMBuild_20150916/VirtualBox/IE9/IE9.Win7.VirtualBox.zip"
BINARIES = "./binaries/"

logger = logging.getLogger()


class SetupFormatter(logging.Formatter):
    def __init__(self):
        logging.Formatter.__init__(self, "[%(asctime)s] [%(bullet)s] %(message)s", None)

    def format(self, record):
        if record.levelno == logging.INFO:
            record.bullet = "*"
        elif record.levelno == logging.DEBUG:
            record.bullet = "+"
        elif record.levelno == logging.WARNING:
            record.bullet = "!"
        else:
            record.bullet = "-"

        return logging.Formatter.format(self, record)


def download_win7():
    ova = "IE9 - Win7.ova"
    vmdk = "IE9 - Win7-disk1.vmdk"
    logger.info("Creating workers directory...")
    try:
        os.mkdir(WORKERS_DIR)
    except OSError:
        pass

    logger.info(f"Downloading {WIN7_URL}")
    wget.download(WIN7_URL, out=WORKERS_DIR)

    logger.info("Extracting zipfile...")
    with zipfile.ZipFile(f"{WORKERS_DIR}/{WIN7_URL.split('/')[-1]}", "r") as zip_ref:
        zip_ref.extractall(WORKERS_DIR)

    logger.info("Extracting tarfile...")
    with tarfile.open(f"{WORKERS_DIR}/{ova}") as tar_ref:
        tar_ref.extract(vmdk, WORKERS_DIR)

    logger.info("Converting vmdk disk to qcow2 image...")
    os.system(f'qemu-img convert -O qcow2 "{WORKERS_DIR}/{vmdk}" "{BASE_QCOW2}"')

    logger.info("Removing temporary files...")
    try:
        os.remove(f"{WORKERS_DIR}/{ova}")
        os.remove(f"{WORKERS_DIR}/{vmdk}")
        os.remove(f"{WORKERS_DIR}/{WIN7_URL.split('/')[-1]}")
    except:
        logger.error("Could not delete files.")


def ssh_connect(ssh):
    logger.info("Trying to connect to Windows OpenSSH server...")
    for i in range(10):
        try:
            sleep(10)
            logger.debug(f"Try number {i}/10.")
            ssh.connect(
                hostname=HOST,
                port=SSH_PORT,
                username=SSH_USERNAME,
                password=SSH_PASSWORD,
                banner_timeout=30,
            )
            logger.info("Successfully connected!")
            return True
        except (
            paramiko.ssh_exception.NoValidConnectionsError,
            paramiko.ssh_exception.SSHException,
            socket.timeout,
        ):
            pass
    return False


def wait_reboot(ssh):
    logger.info("Waiting for Windows reboot...")
    while True:
        try:
            ssh.exec_command("echo 1", timeout=1)
            sleep(10)
        except:
            break
    logger.info("Windows VM just rebooted!")


def copy_files_to_vm(ssh):
    logger.info("Copying files into the Windows VM...")
    try:
        scp = SCPClient(ssh.get_transport())
        scp.put(BINARIES, recursive=True, remote_path=WINDOWS_PATH)
        scp.close()
    except:
        logger.error("Could not copy files to the VM!")


def send_ssh_cmd(ssh, cmd, readline=True):
    _, stdout, stderr = ssh.exec_command(cmd)
    if readline:
        stdout = stdout.readlines()
        stderr = stderr.readlines()
        logger.debug(stdout)
        logger.debug(stderr)
        return stdout


def disable_service(ssh, svc):
    # Make sure the service is disabled before trying to stop it (to avoid TOCTOU)
    logger.info(f"Disabling Windows service: {svc}")
    send_ssh_cmd(ssh, f'cmd.exe /c "sc config {svc} start= disabled"')
    logger.info(f"Stopping Windows service: {svc}")
    send_ssh_cmd(ssh, f'cmd.exe /c "net stop {svc}"')


def create_autodetours_svc(ssh):
    logger.info("Creating AutoDetours service...")
    send_ssh_cmd(ssh, f"cd {WINDOWS_PATH} && chmod +x AutoDetoursAgent.exe")

    send_ssh_cmd(
        ssh,
        'cmd.exe /c "sc create AgentDetours start= auto binPath= C:\\Temp\\AutoDetoursAgent.exe"',
    )


def install_dependencies(ssh):
    logger.info("Installing AutoDetours dependencies...")
    send_ssh_cmd(ssh, f'cd {WINDOWS_PATH} && cmd.exe /c "start /wait 7z-setup.exe /S"')
    send_ssh_cmd(
        ssh,
        f'cd {WINDOWS_PATH} && cmd.exe /c "start /wait dotnetframeworkinstaller.exe /q"',
        readline=False,
    )


def check_agent_state(ssh):
    logger.info("Checking if AutoDetours service is running...")
    stdout = send_ssh_cmd(ssh, 'cmd.exe /c "sc query AgentDetours"')
    if "RUNNING" not in stdout[3]:
        return False
    return True


def make_snapshot():
    logger.info("Making a qemu snaphsot through QMP...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, QMP_PORT))
        logger.debug(sock.recv(1024))

        sock.send(b'{ "execute": "qmp_capabilities" }')
        logger.debug(sock.recv(1024))

        logger.info("Starting the snaphot...")
        snap = json.dumps(
            {
                "execute": "human-monitor-command",
                "arguments": {
                    "command-line": 'migrate "exec: gzip -c > /image/snapshot.gz"'
                },
            }
        )
        snap = bytes(snap, encoding="ascii")
        sock.send(snap)
        logger.debug(sock.recv(1024))

        while True:
            sock.send(b'{ "execute": "query-migrate" }')
            resp = sock.recv(1024)
            logger.debug(resp)
            if b'"status": "completed"' in resp:
                break
            sleep(5)
        logger.info("Snapshot is done!")
        logger.info("Quitting...")
        sock.send(b'{ "execute": "quit" }')
        logger.debug(sock.recv(1024))
        sock.close()
    except:
        return False
    return True


def snapshot_generation(ssh):
    if not ssh_connect(ssh):
        logger.error("Could not connect to OpenSSH server !")
        exit(1)

    if not check_agent_state(ssh):
        logger.error("Agent doesn't seems to be running!")
        exit(1)

    make_snapshot()


def qcow2_generation(ssh):
    if not ssh_connect(ssh):
        logger.error("Could not connect to OpenSSH server !")
        exit(1)

    copy_files_to_vm(ssh)

    # Disable Windows Updates Service
    disable_service(ssh, "wuauserv")
    # Disable Windows Defender
    disable_service(ssh, "windefend")

    create_autodetours_svc(ssh)
    install_dependencies(ssh)

    wait_reboot(ssh)

    if not ssh_connect(ssh):
        logger.error("Could not connect to OpenSSH server!")
        exit(1)

    if not check_agent_state(ssh):
        logger.error("Agent doesn't seems to be running!")
        exit(1)

    send_ssh_cmd(ssh, 'cmd.exe /c "shutdown /s /t 0"')


def build_qemu_image(client):
    logger.info("Building qemu docker image...")
    try:
        client.images.get("autodetours_qemu")
    except docker.errors.ImageNotFound:
        client.images.build(tag="autodetours_qemu", path="./qemu")
        return
    logger.info("Image not rebuilt because it already exists.")


def run_qemu_container(client, snapshot_mode=False):
    logger.info("Running qemu container...")
    cmd = [
        "-nographic",
        "-monitor none",
        "-hda /image/win7.qcow2",
        "-m 1024",
        "--enable-kvm",
        "-net nic",
        f"-net user,hostfwd=tcp:{HOST}:{SSH_PORT}-:22",
        f"-qmp tcp:{HOST}:{QMP_PORT},server,nowait",
    ]
    if snapshot_mode:
        cmd.append("-snapshot")

    cmd = " ".join(cmd)
    client.containers.run(
        QEMU_IMAGE,
        command=cmd,
        network_mode="host",
        devices=["/dev/kvm"],
        volumes={WORKERS_DIR: {"bind": "/image", "mode": "rw"}},
        name=INSTALL_CONTAINER,
        remove=True,
        detach=True,
        privileged=True,
    )


def wait_qemu_container(client):
    logger.info("Waiting for container deletion...")
    ok = False
    for _ in range(10):
        try:
            client.containers.get(INSTALL_CONTAINER)
            sleep(10)
        except docker.errors.NotFound:
            ok = True
            break
    if not ok:
        logger.error("Issue encountered when waiting for container ending...")
        exit(1)


def clean(complete_clean):
    if complete_clean:
        logger.info("Removing /workers directory...")

        def remove_readonly(func, path, _):
            "Clear the readonly bit and reattempt the removal"
            os.chmod(path, stat.S_IWRITE)
            func(path)

        rmtree(WORKERS_DIR, onerror=remove_readonly)
    else:
        logger.info("Removing previous image and snapshot...")
        if os.path.isfile(os.path.join(WORKERS_DIR, WORKER_QCOW2)):
            os.remove(os.path.join(WORKERS_DIR, WORKER_QCOW2))
        if os.path.isfile(os.path.join(WORKERS_DIR, WORKER_SNAPSHOT)):
            os.remove(os.path.join(WORKERS_DIR, WORKER_SNAPSHOT))


def generate_django_secret():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    secret_key = "".join(secrets.choice(chars) for i in range(50))
    return secret_key


def generate_postgres_password():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*-_=+"
    secret_key = "".join(secrets.choice(chars) for i in range(16))
    return secret_key


def update_env_file(nbr_workers):
    logger.info(f"Updating {ENV_FILE} configuration file...")
    text = f"""DEBUG={"True" if DEV else "False"}
SECRET_KEY='{generate_django_secret()}'

POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD='{generate_postgres_password()}'
POSTGRES_HOST=db
POSTGRES_PORT=5432

CELERY_TASKS_SCHEDULE=10.0

NB_WIN7_WORKERS={nbr_workers}
WIN7_IMAGES_DIR={WORKERS_DIR}
"""
    with open(ENV_FILE, "w") as fd:
        fd.write(text)


def main(args):
    """Setup the project

    1. Download the Windows 7 VM
    2. Convert the Windows 7 VM (ova) in qcow2 format
    3. Build the qemu container image
    1. Launch win7.qcow2 with a qemu container
    2. Connect to OpenSSH
    3. Install the agent and its dependecies:
        - Disable Windows Defender
        - Disable Windows Updates
        - Install 7zip
        - Install .Net 4.7.2 framework
        - Create the Agent Windows Service
    4. Wait for reboot to finish the installation
    5. Connect to OpenSSH
    6. Shutdown the system (wait for container deletion)
    7. Launch win7.qcow2 in -snapshot mode with a qemu container
    8. Connect to OpenSSH
    9. Check if the agent is running
    10. Create an external snapshot

    Args:
        args (Object): Setup args from argparser
    """
    handler = logging.StreamHandler(sys.stdout)
    docker_client = docker.DockerClient(base_url=DOCKER_SOCKET)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    DEV = args.dev

    handler.setFormatter(SetupFormatter())
    logger.addHandler(handler)
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.info("Starting the installation...")

    clean(args.clean)

    if not os.path.exists(BASE_QCOW2):
        download_win7()
    logger.info("Copying the base.qcow2 image to win7.qcow2...")
    copyfile(BASE_QCOW2, WORKERS_DIR + "/" + WORKER_QCOW2)

    build_qemu_image(docker_client)
    run_qemu_container(docker_client, snapshot_mode=False)
    qcow2_generation(ssh)

    wait_qemu_container(docker_client)
    run_qemu_container(docker_client, snapshot_mode=True)

    snapshot_generation(ssh)

    update_env_file(args.workers)

    logger.info("Done!")
    print("\n")
    logger.info("You can now start the project using: docker-compose up -d")


if __name__ == "__main__":
    HEADER = """

    ___         __        ____       __
   /   | __  __/ /_____  / __ \___  / /_____  __  ____________
  / /| |/ / / / __/ __ \/ / / / _ \/ __/ __ \/ / / / ___/ ___/
 / ___ / /_/ / /_/ /_/ / /_/ /  __/ /_/ /_/ / /_/ / /  (__  )
/_/  |_\__,_/\__/\____/_____/\___/\__/\____/\__,_/_/  /____/
==============================================================

"""
    print(HEADER)
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
AutoDetours is an application allowing to trace syscalls from multiple samples at the same time.
The goal is to be able to generate a large dataset of Windows API calls by malwares.
This dataset could then be used in machine learning to try to classify samples by families.
To provide this solution we are using Detours project from Microsoft.""",
    )
    parser.add_argument(
        "--dev",
        help="Setup the environment for development",
        action="store_true",
    )
    parser.add_argument(
        "--debug", help="Run installation in debug mode", action="store_true"
    )
    parser.add_argument(
        "-c", "--clean", help="Clean all qcow2 images", action="store_true"
    )
    parser.add_argument(
        "-w",
        "--workers",
        required=True,
        type=int,
        help="Number of simultaneous workers (1GB RAM / worker)",
    )
    args = parser.parse_args()
    main(args)
