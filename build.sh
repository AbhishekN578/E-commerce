#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if it doesn't exist (Optional, but useful for first deployment)
# DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --no-input --username admin --email admin@example.com || true
