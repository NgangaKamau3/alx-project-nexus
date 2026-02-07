#!/bin/bash
set -e

echo "Deployment Script for Modestwear.."

echo "Migrating to database.."
python manage.py migrate

echo "Collecting static files ..."
python manage.py collectstatic --noinput

echo "Starting Celery worker .."
celery -A core worker --pool=gevent --concurrency=4 --loglevel=info & 
echo "Starting Gunicorn server.."
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT