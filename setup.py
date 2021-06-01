import paramiko
import socket
import json

from scp import SCPClient
from os import system
from subprocess import Popen, PIPE
from time import sleep


def check_dependancies():
    # qemu wget 
    pass


def download_win7():
    system("""
    download_link="https://az792536.vo.msecnd.net/vms/VMBuild_20150916/VirtualBox/IE9/IE9.Win7.VirtualBox.zip"
    downloaded="IE9.Win7.VirtualBox.zip"
    ova="IE9 - Win7.ova"
    ovf="IE9 - Win7.ovf"
    vmdk="IE9 - Win7-disk1.vmdk"
    qcow2="output.qcow2"
    curl -O "$download_link"
    unzip "$downloaded"
    tar xfv "$ova"
    qemu-img convert -O qcow2 "$vmdk" "$qcow2"
    mkdir workers
    mv "$qcow2" workers
    rm -f "$downloaded" "$ova" "$ovf" "$vmdk"
    """)

def snapshot_generation():
    p = Popen(
        [
            "qemu-system-x86_64",
            "-hda", "workers/output.qcow2",
            "-m", "1024",
            "--enable-kvm",
            "-net", "nic",
            "-net", "user,hostfwd=tcp::2222-:22",
            "-monitor", "none",
            "-qmp", "tcp:127.0.0.1:2223,server,nowait"
        ],
        stdout=PIPE,
        stdin=PIPE
    )

    sleep(15)


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for _ in range(10):
        try:
            sleep(10)
            ssh.connect(hostname='127.0.0.1', port=2222, username='IEUser', password='Passw0rd!')
            break
        except (paramiko.ssh_exception.NoValidConnectionsError, paramiko.ssh_exception.SSHException):
            pass

    scp = SCPClient(ssh.get_transport())
    scp.put('./executables/', recursive=True, remote_path='/cygdrive/c/Temp')
    scp.close()


    # Make sure the service is disabled before trying to stop it (to avoid TOCTOU)
    stdin, stdout, stderr = ssh.exec_command('cmd.exe /c "sc config wuauserv start= disabled"')
    print(stdout.readlines(), stderr.readlines())
    ssh.exec_command('cmd.exe /c "sc config windefend start= disabled"')
    stdin, stdout, stderr = ssh.exec_command('cmd.exe /c "net stop wuauserv"')
    print(stdout.readlines(), stderr.readlines())
    ssh.exec_command('cmd.exe /c "net stop windefend"')

    stdin, stdout, stderr = ssh.exec_command('cd /cygdrive/c/Temp/ && chmod +x agent/AutoDetoursAgent.exe')
    print(stdout.readlines(), stderr.readlines())
    stdin, stdout, stderr = ssh.exec_command('cmd.exe /c "sc create AgentDetours start= auto binPath= C:\\Temp\\agent\\AutoDetoursAgent.exe"')
    print(stdout.readlines(), stderr.readlines())
    stdin, stdout, stderr = ssh.exec_command('cd /cygdrive/c/Temp/ && cmd.exe /c "start /wait 7z-setup.exe /S"')
    print(stdout.readlines(), stderr.readlines())
    ssh.exec_command('cd /cygdrive/c/Temp/ && cmd.exe /c "start /wait dotnetframeworkinstaller.exe /q"', timeout=20) # can't get output, the command remain busy even after restart


    print("Waiting for reboot...")
    while True:
        try:
            ssh.exec_command('echo 1', timeout=1)
            sleep(2)
        except:
            break
    print("VM reboot detected !")


    for _ in range(10):
        try:
            sleep(10)
            ssh.connect(hostname='127.0.0.1', port=2222, username='IEUser', password='Passw0rd!')
            break
        except (paramiko.ssh_exception.NoValidConnectionsError, paramiko.ssh_exception.SSHException):
            pass
    sleep(5)
    stdin, stdout, stderr = ssh.exec_command('cmd.exe /c "sc query AgentDetours"')
    if "RUNNING" not in stdout.readlines()[3]:
        print("Error")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 2223))
    print(sock.recv(1024))
    sock.send(b'{ "execute": "qmp_capabilities" }')
    print(sock.recv(1024))
    sock.send(b'{ "execute": "query-status" }')
    print(sock.recv(1024))
    snap = json.dumps({ "execute": "human-monitor-command", "arguments": { "command-line": "savevm agent" } })
    snap = bytes(snap, encoding='ascii')
    sock.send(snap)
    print(sock.recv(1024))
    while True:
        sock.send(b'{ "execute": "query-status" }')
        a = sock.recv(1024)
        print(a)
        if b'"status": "running"' in a:
            break
        sleep(5)
    sock.send(b'{ "execute": "quit" }')
    p.wait()


def main():
    #download_win7()
    snapshot_generation()

if __name__ == "__main__":
    main()