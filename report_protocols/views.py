from django.shortcuts import render
from models import Protocol

def protocolTable(request):
    protocols = Protocol.objects.all().order_by("-timesUsed","name")
    context_dict={}
    context_dict['protocols']=protocols
    return render(request, 'report_protocols/protocolsTable.html', context_dict)

def scipionUsage(request):
    return render(request, 'report_protocols/scipionUsage.html')
