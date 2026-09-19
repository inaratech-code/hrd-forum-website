#!/bin/bash
set -e
echo "Building HRD Forum for Vercel..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput
# Migrations are not run on every request; opt-in via RUN_MIGRATE_ON_BOOT=1.
if [ "${RUN_MIGRATE_ON_BOOT}" = "1" ] || [ "${RUN_MIGRATE_ON_BOOT}" = "true" ]; then
  python3 manage.py migrate --noinput
fi
