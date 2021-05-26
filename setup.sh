#!/bin/bash

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
mv "$qcow2" /workers

rm -f "$downloaded" "$ova" "$ovf" "$vmdk"

echo qemu image has been generated as "$qcow2"
