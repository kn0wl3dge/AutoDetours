<p align="center">
  <img width="200" height="200" src="doc/logoyellow.png">
</p>

[![BackendCI](https://github.com/Kn0wl3dge/AutoDetours/actions/workflows/backend.yml/badge.svg)](https://github.com/Kn0wl3dge/AutoDetours/actions/workflows/backend.yml)
# AutoDetours

*/!\ This project isn't ready for production /!\\*

## Introduction

AutoDetours is a scalable application for Windows malware analysis.
For the moment only PESieve and Detours are integrated.

[PESieve](https://github.com/hasherezade/pe-sieve) job goal is to unpack a Windows PE malware.  
[Detours](https://github.com/microsoft/Detours) job goal is to hook syscalls called by a Windows PE malware. 

On the one hand, this application could be used as an analysis pipeline for Windows malware.  
On the other hand, it could be used to generate a large dataset which can contains results from differents tools.
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
To install the project, run the following commands:
```python
pip3 install -r requirements.txt
python3 setup.py -w <nbr_workers>
```

You can also use the option `--dev` to configure the project for developement.

## Running the projet
To run the project, just use the following command:

```
docker-compose up -d
```

## Usage
You can now launch the app on your favorite Browser and upload your samples. Once the treatment is done you can download the results list (in a JSON format) on your computer.
The application should be available at http://172.20.0.10/
