from django.shortcuts import render
from django.conf import settings
import django

def index(request):
    """Landing page for the API"""
    context = {
        'django_version': django.get_version(),
        'base_url': request.build_absolute_uri('/').rstrip('/')
    }
    return render(request, 'index.html', context)
