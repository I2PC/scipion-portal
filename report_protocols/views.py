from django.shortcuts import render
from report_protocols.models import Protocol, ProtocolType, Package


def protocolTable(request):
    protocols = Protocol.objects.all().order_by("-timesUsed", "name")
    context_dict = {'protocols': protocols}
    return render(request, 'report_protocols/protocolsTable.html', context_dict)


def projectStats(request):
    return render(request, 'report_protocols/projectStats.html')


def installationStats(request):
    return render(request, 'report_protocols/installationStats.html')


def protocolTypes(request):
    types = ProtocolType.objects.all()
    context_dict = {'types': types}
    return render(request, 'report_protocols/protocolTypes.html', context_dict)


def packages(request):
    context_dict = {}
    context_dict['packages'] = Package.objects.all().order_by("name")
    return render(request, 'report_protocols/packages.html', context_dict)
