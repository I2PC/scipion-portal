#!/usr/bin/python
# **************************************************************************
# *
# * Authors:    Jose Gutierrez (jose.gutierrez@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************

import os
import json
import calendar
import socket
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from ip_address import get_geographical_information, get_client_ip

try:
    from wsgiref.util import FileWrapper
except ImportError:
    from django.core.servers.basehttp import FileWrapper

from django.forms.models import model_to_dict
from django.http import JsonResponse
from web.models import Acknowledgement
from report_protocols.models import Package


# noinspection PyUnusedLocal
def home(request):
    # Get the packages
    return render(request,'home/index.html')


# noinspection PyUnusedLocal
def biologists(request):
    context = {}

    # Get the packages
    packages = Package.objects.all()
    context['packages'] = packages
    return render(request,'home/biologists.html', context)


# noinspection PyUnusedLocal
def facilities(request):

    return render(request,'home/facilities.html')


# noinspection PyUnusedLocal
def developers(request):

    return render( request,'home/developers.html')

def contact(request):

    packages = Package.objects.order_by("name")

    context = {
        "packages": packages,
    }
    return render( request,'home/contactus.html', context)


def utc_to_local(utc_dt):
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    return local_dt.replace(microsecond=utc_dt.microsecond)


def getPluginsDict():
    result = {}
    for plugin in Package.objects.all():
        pluginDict = model_to_dict(plugin, exclude=["logo", "description", "url"])
        if pluginDict['pipName'] != "":
            result[pluginDict['pipName']] = pluginDict
    return result


# noinspection PyUnusedLocal
def getPluginsJSON(request):
    return JsonResponse(getPluginsDict(), json_dumps_params={'indent': 4})


# noinspection PyUnusedLocal
def acknowledgements(request):
    acks = Acknowledgement.objects.all()
    context_dict = {'acknowledgements': acks}
    return render( request,'home/acknowledgements.html', context_dict)
