from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("report_protocols says hey there partner!")

def whoami(request):

    sex = request.GET['sex']
    name = request.GET['name']

    response = 'You are ' + name + ' and of sex ' + sex

    return HttpResponse(response)