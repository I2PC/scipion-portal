from django.shortcuts import render
from django.http import HttpResponse
from models import Protocol

def index(request):
    return HttpResponse("report_protocols says hey there partner!")

def protocolTable(request):
    protocols = Protocol.objects.all().order_by("-timesUsed","name")
    context_dict={}
    context_dict['protocols']=protocols
    return render(request, 'report_protocols/protocolsTable.html', context_dict)