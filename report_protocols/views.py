from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("report_protocols says hey there partner!")
