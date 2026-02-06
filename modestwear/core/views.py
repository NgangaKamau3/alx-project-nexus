from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("ModestWear API - Visit /test-api/ to test endpoints")

def api_tester(request):
    return render(request, 'api_tester.html')