#!/bin/bash
set -e

echo "Deployment Script for Modestwear.."

echo "Migrating to database.."
python manage.py migrate

echo "Creating superuser if needed.."
python manage.py create_superuser

echo "Collecting static files ..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server.."
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --graceful-timeout 30 --keep-alive 5