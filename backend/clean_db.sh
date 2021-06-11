#!/bin/sh

rm -vf celerybeat-schedule
rm -vrf malware/migrations/
rm -vrf workers/migrations/

mkdir malware/migrations/
mkdir workers/migrations/

touch malware/migrations/__init__.py
touch workers/migrations/__init__.py
