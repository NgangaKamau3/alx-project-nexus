from django.shortcuts import render
from django.conf import settings

def social_auth_test(request):
    return render(request, 'social_auth_test.html', {
        'google_client_id': settings.GOOGLE_CLIENT_ID
    })
