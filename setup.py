import argparse
import docker
import json
import logging
import os
import paramiko
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
HOST = "127.0.0.1"
SSH_PORT = 2222
QMP_PORT = 2223
DOCKER_SOCKET = "unix://var/run/docker.sock"
WORKERS_DIR = os.path.dirname(os.path.realpath(__file__)) + "/workers"
BASE_QCOW2 = WORKERS_DIR + "/base.qcow2"
WORKER_QCOW2_FORMAT = "win7-{}.qcow2"
ENV_FILE = ".env.dev"
SSH_USERNAME = "IEUser"
SSH_PASSWORD = "Passw0rd!"
WINDOWS_PATH = "/cygdrive/c/Temp"
QEMU_IMAGE = "autodetours_qemu"
WIN7_URL = "https://az792536.vo.msecnd.net/vms/VMBuild_20150916/VirtualBox/IE9/IE9.Win7.VirtualBox.zip"

logger = logging.getLogger()


class SetupFormatter(logging.Formatter):
    def __init__(self):
        logging.Formatter.__init__(self, "%(bullet)s %(message)s", None)

    def format(self, record):
        if record.levelno == logging.INFO:
            record.bullet = "[*]"
        elif record.levelno == logging.DEBUG:
            record.bullet = "[+]"
        elif record.levelno == logging.WARNING:
            record.bullet = "[!]"
        else:
            record.bullet = "[-]"

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
        scp.put("./binaries/", recursive=True, remote_path=WINDOWS_PATH)
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
    send_ssh_cmd(ssh, f"cd {WINDOWS_PATH} && chmod +x agent/AutoDetoursAgent.exe")

    send_ssh_cmd(
        ssh,
        'cmd.exe /c "sc create AgentDetours start= auto binPath= C:\\Temp\\agent\\AutoDetoursAgent.exe"',
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
                "arguments": {"command-line": "savevm agent"},
            }
        )
        snap = bytes(snap, encoding="ascii")
        sock.send(snap)
        logger.debug(sock.recv(1024))

        while True:
            sock.send(b'{ "execute": "query-status" }')
            resp = sock.recv(1024)
            logger.debug(resp)
            if b'"status": "running"' in resp:
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

    if not make_snapshot():
        logger.error("Could not make the snapshot!")
        exit(1)


def build_qemu_image(client):
    logger.info("Building qemu docker image...")
    try:
        client.images.get("autodetours_qemu")
    except docker.errors.ImageNotFound:
        client.images.build(tag="autodetours_qemu", path="./qemu")
        return
    logger.info("Image not rebuilt because it already exists.")


def run_qemu_container(client):
    logger.info("Running qemu container...")
    cmd = f"-nographic -hda /image/win7-0.qcow2 -m 1024 --enable-kvm -net nic -net user,hostfwd=tcp:{HOST}:{SSH_PORT}-:22 -monitor none -qmp tcp:{HOST}:{QMP_PORT},server,nowait"
    client.containers.run(
        QEMU_IMAGE,
        command=cmd,
        network_mode="host",
        devices=["/dev/kvm"],
        volumes={WORKERS_DIR: {"bind": "/image", "mode": "rw"}},
        name="autodetours_qemu_gen",
        remove=True,
        detach=True,
        privileged=True,
    )


def clean(complete_clean):
    if complete_clean:
        logger.info("Removing /workers directory...")

        def remove_readonly(func, path, _):
            "Clear the readonly bit and reattempt the removal"
            os.chmod(path, stat.S_IWRITE)
            func(path)

        rmtree(WORKERS_DIR, onerror=remove_readonly)
    else:
        logger.info("Removing previous images (win7-xx.qcow2)...")
        os.system(f"rm {WORKERS_DIR}/win7*")


def generate_workers(nbr_workers):
    if nbr_workers > 0:
        for i in range(1, nbr_workers):
            logger.info(f"Generate worker {i}")
            copyfile(
                WORKERS_DIR + "/" + WORKER_QCOW2_FORMAT.format(0),
                WORKERS_DIR + "/" + WORKER_QCOW2_FORMAT.format(i),
            )


def update_env_file(nbr_workers):
    logger.info("Updating .env.dev configuration file...")
    with open(ENV_FILE, "r") as fd:
        lines = fd.readlines()
    for i in range(len(lines)):
        if "NB_WIN7_WORKERS" in lines[i]:
            lines[i] = f"NB_WIN7_WORKERS={nbr_workers}\n"
        elif "WIN7_IMAGES_DIR" in lines[i]:
            lines[i] = f"WIN7_IMAGES_DIR={WORKERS_DIR}\n"
    with open(ENV_FILE, "w") as fd:
        fd.writelines(lines)


def main(args):
    handler = logging.StreamHandler(sys.stdout)
    docker_client = docker.DockerClient(base_url=DOCKER_SOCKET)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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
    logger.info("Copying the base.qcow2 image to win7-0.qcow2...")
    copyfile(BASE_QCOW2, WORKERS_DIR + "/" + WORKER_QCOW2_FORMAT.format(0))

    build_qemu_image(docker_client)
    run_qemu_container(docker_client)
    snapshot_generation(ssh)

    generate_workers(args.workers)
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
        "-d", "--debug", help="Run installation in debug mode", action="store_true"
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
