
</p>

[![BackendCI](https://github.com/Kn0wl3dge/AutoDetours/actions/workflows/backend.yml/badge.svg)](https://github.com/Kn0wl3dge/AutoDetours/actions/workflows/backend.yml)
# AutoDetours

*/!\ This project isn't ready for production /!\\*

## Introduction

AutoDetours is an application allowing the usage of multiples windows toolkit to analyse malware.
For the moment only PESieve and Detours are integrated.

[PESieve](https://github.com/hasherezade/pe-sieve) job goal is to unpack a Windows PE malware.  
[Detours](https://github.com/microsoft/Detours) job goal is to trace a Windows PE malware. 

In one hand, this application could be used as an analysis pipeline for windows malware.  
In other hand, it could be used to generate a large dataset which can contains results from differents tools.
This dataset could then be used in machine learning to try to classify samples by families.

## Architecture
<p align="center">
  <img height="500" src="doc/AutoDetoursArchi.png">
</p>

## Installation

### Prerequisites

- [X] Docker installed and running
- [X] docker-compose
- [X] Python3 for the setup script

### Procedure
Just run `pip3 install -r requirements.txt` and `python3 setup.py -w <nbr_workers>` to install the project.  
This script will download, decompress and convert a Windows7 VM to a qcow2 image.  
Then, it will run the VM inside a container and configure the VM then install the agent and its dependencies.  
It will make a snapshot of the VM and setup the number of workers you want.  
Do not worry, it's going to take some time to finish...

## Running the projet
To run the project, just use the following command:

```
docker-compose up -d
```

## Usage
You can now launch the app on your favorite Browser and upload your samples. Once the treatment is done you can download the results list (in a JSON format) on your computer.
The application should be available at http://172.20.0.10/
