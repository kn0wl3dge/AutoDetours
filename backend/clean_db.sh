#!/bin/sh

rm -vf celerybeat-schedule
rm -vrf malwares/migrations/
rm -vrf workers/migrations/

mkdir malwares/migrations/
mkdir workers/migrations/

touch malwares/migrations/__init__.py
touch workers/migrations/__init__.py
