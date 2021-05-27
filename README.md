
</p>

[![BackendCI](https://github.com/Kn0wl3dge/AutoDetours/actions/workflows/backend.yml/badge.svg)](https://github.com/Kn0wl3dge/AutoDetours/actions/workflows/backend.yml)
# AutoDetours

/!\ This project isn't ready for production:
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
- [X] Python3 installed
- [X] Agent installed in a qcow2 Win7 image (+ .Net Framework 4.7.2)

### Creating the VM with the Agent

The whole setup should take less than 10 minutes with a correct Internet connection.

- Run `./setup.sh all`. For your information, this script will:
    1. Same as `./setup.sh qemu`
        * Download a Windows IE9 VirtualBox VM (https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/)
        * Unzip the VM and the untar the ova file
        * Convert the VMDK into a qcow2 image
    2. Same as `./setup.sh zip`
        * Zip the `executables` folder to `executables.zip`
    3. Same as `./setup.sh serv`
        * Open a local Python HTTP server on port 4444

- Run the qemu image using `qemu-system-i386 -monitor stdio -show-cursor -m 1024 -enable-kvm -hda output.qcow2` and wait 15 to 30 seconds.
- Open Internet Explorer and go to [http://yourhostlocalIP:4444/executables.zip](http://yourhostlocalIP:4444/executables.zip). Download it and extract it in `C:\Temp`. It MUST look like this:

<p align="center">
  <img height="500" src="doc/TempArchi.png">
</p>

- Run `dotnetframeworkinstaller.exe` to install the .Net Framwork Runtime 4.7.2
- Run `7z-setup.exe` with the default path for installation to install 7z
- Disable the Windows Firewall and the Windows AntiVirus:
    * Type `firewall`, open `Windows Firewall`, then on the left `Turn Windows Firewall on or off` and turn off both protections.
    * Type `defender`, open `Windows Defender`, then `Tools` -> `Options`, and disable `Automatic Scanning` and `Real-Time Protection`
- Run the `startAgent.bat` script **AS ADMINISTRATOR**
- Take a snapshot of the running VM using `savevm agent` (in qemu console on host)
- Build the qemu image by running the following command in the `qemu/` directory: `docker build -t qemu .`

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
The application should be available at http://172.20.0.10/
