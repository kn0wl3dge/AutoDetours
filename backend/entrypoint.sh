#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

echo "Creating /data dirs"
[ ! -d "/data/datasets" ] && mkdir /data/datasets
[ ! -d "/data/rules" ] && mkdir /data/db_rules
[ ! -d "/data/malwares" ] && mkdir /data/malwares

echo "Starting Django"
python manage.py flush --no-input
python manage.py makemigrations --no-input
python manage.py migrate --no-input

exec "$@"
