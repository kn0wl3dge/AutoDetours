#!/bin/sh

rm -vf celerybeat-schedule
rm -vrf malwares/migrations/
rm -vrf workers/migrations/
rm -vrf jobs/migrations/

mkdir malwares/migrations/
mkdir workers/migrations/
mkdir jobs/migrations/

touch malwares/migrations/__init__.py
touch workers/migrations/__init__.py
touch jobs/migrations/__init__.py

python manage.py flush --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput