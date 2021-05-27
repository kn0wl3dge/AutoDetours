#!/bin/bash

create_qemu ()
{
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
    echo qemu image has been generated as "$qcow2"
}

create_zip ()
{
    exec="executables"
    zipfile="$exec.zip"
    rm -fv "$zipfile"
    zip -r "$zipfile" "$exec"
    echo zipped "$exec" to "$zipfile"
}

open_serv ()
{
    python3 -m http.server 4444
}

do_all ()
{
    create_qemu
    create_zip
    open_serv
}

display_help ()
{
    echo "./setup.sh [arg]

        all     - do everything
        qemu    - create qemu image from VirtualBox ova
        zip     - zip the required file for the qemu
        serv    - open local server on 4444 to transfer files to qemu"
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ];
then
    display_help
    exit 1
fi

case "$1" in
    "all")          do_all;;
    "qemu")         create_qemu;;
    "zip")          create_zip;;
    "serv")         open_serv;;
    *)              display_help;;
esac
