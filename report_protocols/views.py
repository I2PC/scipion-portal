from django.shortcuts import render
from models import Protocol, ProtocolType, Package


def protocolTable(request):
    protocols = Protocol.objects.all().order_by("-timesUsed","name")
    context_dict = {}
    context_dict['protocols'] = protocols
    return render(request, 'report_protocols/protocolsTable.html', context_dict)

def scipionUsage(request):
    return render(request, 'report_protocols/scipionUsage.html')

def protocolTypes(request):
    types = ProtocolType.objects.all()
    context_dict = {}
    context_dict['types'] = types
    return render(request, 'report_protocols/protocolTypes.html', context_dict)

def packages(request):
    types = Package.objects.all()
    context_dict = {}
    context_dict['packages'] = types
    return render(request, 'report_protocols/packages.html', context_dict)
