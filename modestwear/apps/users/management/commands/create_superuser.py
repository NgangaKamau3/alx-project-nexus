from django.core.management.base import BaseCommand
from apps.users.models import User
import os

class Command(BaseCommand):
    help = 'Create a superuser if none exists'

    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True).exists():
            email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@modestwear.com')
            password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
            username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
            
            User.objects.create_superuser(
                email=email,
                password=password,
                username=username
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))
