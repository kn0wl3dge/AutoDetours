# AutoDetours
AutoDetours is an application which permit to analyze malwares and to provide
for each of them a card index about systems calls.  
To provide this solution we are using `Detour`  from Microsoft.  

The provided solution contains an agent which permit to treat all the malwares.

## Installation
First of all the installation can just be done on windows for the agent.  
To host the application (nginx-server) you can use an other OS like linux or
MacOS.

### Prerequisites

- [X] Docker installed
- [X] VSCode with C# packages installed
- [X] Agent installed in a qcow2 Win7 image (+ .Net Framework 4.7.2)

### Building the VM with the Agent

#### Build
- Open the Agent project in VSCode and generate the solution for x86 if using Windows 7 32bits

#### Installation
- Download a Windows IE VirtualBox VM (https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/)
- Unzip the VM and the untart the ova file
- Convert the VMDK into a qcow2 image using `qemu-img convert -O qcow2 input.vmdk output.qcow2`
- Run the VM using qemu : `.\qemu-system-i386.exe -monitor stdio -show-cursor -m 1024 -hda output.qcow2`
- Copy the agent and its dependancies into the directory C:\\Temp\\agent of the Win7 VM (using qemu)
- Copy files in the folder hooking into the directory C:\\Temp of the Win7 VM (using qemu)
- Create a Windows Service (`sc create "Agent Detours" start= auto binPath= "C:\Temp\agent\AutoDetoursAgent.exe"`
- Launch the service (`sc start "Agent Detours"`)
- Take a snapshot of the running VM using `savevm agent`

### Running the projet
To run the project you must use the `docker-compose.yml` in the root folder
of the project with the command:
```
docker-compose up
```

**Warning**: If there is an error during the docker compose command, you can
rebuild the docker with the command:
```
docker-compose build
```

## Usage
You can now launch the app on your favorite Browser `#Brave <3` and upload a
malware. Once the treatment is done you can dowload the result list on your
computer.
The application should be available at http://ip:80

## Main Contributors
- [Radion94200](https://github.com/Radion94200)
- [Prolintos](https://github.com/Prolintos)
- [Deacllock](https://github.com/Deacllock)
- [Kn0wl3dge](https://github.com/Kn0wl3dge)
