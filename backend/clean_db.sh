#!/bin/sh

rm -vf celerybeat-schedule
rm -vrf malwaredb/migrations/
rm -vrf workers/migrations/

mkdir malwaredb/migrations/
mkdir workers/migrations/

touch malwaredb/migrations/__init__.py
touch workers/migrations/__init__.py
