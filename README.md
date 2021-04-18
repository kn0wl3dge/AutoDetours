<p align="center">
  <img width="200" height="200" src="doc/logoyellow.png">
</p>

[![BackendCI](https://github.com/Kn0wl3dge/AutoDetours/actions/workflows/backend.yml/badge.svg)](https://github.com/Kn0wl3dge/AutoDetours/actions/workflows/backend.yml)
# AutoDetours

/!\ This project isn't ready for production:
* The sandbox doesn't isolate the network so any malware executed in this environment may communicate with the private network or with internet!
* The API code needs some refacto and vulnerability fix (unlimited dataset generation without cleanup, killing any container from a fake worker and more)

## Introduction

AutoDetours is an application allowing to trace syscalls from multiple samples at the same time.

The goal is to be able to generate a large dataset of Windows API calls by malwares.
This dataset could then be used in machine learning to try to classify samples by families.
To provide this solution we are using [Detours](https://github.com/microsoft/Detours) project from Microsoft.

## Architecture
<p align="center">
  <img height="500" src="doc/AutoDetoursArchi.png">
</p>


## Installation

### Prerequisites

- [X] Docker installed
- [X] Agent installed in a qcow2 Win7 image (+ .Net Framework 4.7.2)

### Creating the VM with the Agent
- Download a Windows IE9 VirtualBox VM (https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/)
- Unzip the VM and the untart the ova file
- Convert the VMDK into a qcow2 image using `qemu-img convert -O qcow2 input.vmdk output.qcow2`
- Run the VM using qemu : `qemu-system-i386 -monitor stdio -show-cursor -m 1024 -enable-kvm -hda output.qcow2`
- Copy files from the folder hooking into the directory C:/Temp of the Win7 VM (using qemu)
- Install the .Net Framwork Runtime 4.7.2
- Disable the Windows Firewall and the Windows AntiVirus
- Start a cmd.exe with admin privileges
- Create a Windows Service (`sc create "Agent Detours" start= auto binPath= "C:\Temp\agent\AutoDetoursAgent.exe"`
- Launch the service (`sc start "Agent Detours"`)
- Take a snapshot of the running VM using `savevm agent` (in qemu)

### Running the projet
Now rename your image `win7-0.qcow2`. If you want multiple workers (so you can have multiple analysis at the same time), copy/paste the qemu image.
For example, if you need 3 workers, you'll have in you directory:
- win7-0.qcow2
- win7-1.qcow2
- win7-2.qcow2

Then, update the `.env.dev` file to you need. You should at least specify the number of workers you have and the associated directory.

To run the project you must use the `docker-compose.yml` in the root folder
of the project with the command:
```
docker-compose up
```

## Usage
You can now launch the app on your favorite Browser and upload your samples. Once the treatment is done you can download the results list (in a JSON format) on your computer.
The application should be available at http://localhost:80

## Main Contributors
- [Radion94200](https://github.com/Radion94200)
- [Prolintos](https://github.com/Prolintos)
- [Deacllock](https://github.com/Deacllock)
- [Kn0wl3dge](https://github.com/Kn0wl3dge)
