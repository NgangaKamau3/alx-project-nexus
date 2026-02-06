#!/bin/bash
set -e

echo "Deployment Script for Modestwear.."
# Pull latest code
git pull origin main


echo "Migrating to database.."
python manage.py migrate

echo "Collecting static files ..."
python manage.py collectstatic --noinput

echo "Starting Celery worker .."
celery -A core worker --concurrency=2 --loglevel=info & 
echo "Starting Gunicorn server.."
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT



# Build and deploy with Docker
docker build -t modestwear:latest .
docker stop modestwear || true
docker rm modestwear || true

docker run -d \
  --name modestwear \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=core.settings_prod \
  -e DB_PASSWORD=$DB_PASSWORD \
  -e SECRET_KEY=$SECRET_KEY \
  -e SENTRY_DSN=$SENTRY_DSN \
  modestwear:latest

# Run migrations
docker exec modestwear python manage.py migrate

echo "✅ Deployment completed successfully!"