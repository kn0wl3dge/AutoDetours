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
[x] Docker installed on windows
[x] Create C/Temp/ folder in windows
[x] Move files `hooking/*.exe` in the previous file
[x] VSCode with C# packages installed

### Launching Agent
Before building the agent update the ip adress in the `AgentService.cs` file
at the class `Constants`.

#### Build
- Open the project in VSCode and generate the solution.

#### Installation
- Open VSConsole as administrator and install the service previously created
with the command:
```
InstallUtil AutoDetoursAgent.exe
```

#### Uninstall
- Open VSConsole as administrator and uninstall the service with the command:
```
InstallUtil /u AutoDetoursAgent.exe
```

### Docker
To launch the docker you must use the `docker-compose.yml` in the root folder
of the project with the command:
```
docker-compose up
```

**Attention**: If there is an error during the docker compose command, you can
rebuild the docker with the command:
```
docker-compose build
```

Once the docker installed you can launch it in the windows docker interface and
wait it starts.

### Try the app
You can now launch the app on your favorite Browser `#Brave <3` and upload a
malware. Once the treatment is done you can dowload the result list on your
computer.

## Main Contributors
- [Radion94200](https://github.com/Radion94200)
- [Prolintos](https://github.com/Prolintos)
- [Deacllock](https://github.com/Deacllock)
- [Kn0wl3dge](https://github.com/Kn0wl3dge)
