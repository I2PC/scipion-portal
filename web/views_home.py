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
from datetime import datetime, timedelta, tzinfo
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.template.context_processors import csrf
# Depending on DJANGO version (first is for DJANGO 1.9) second for 1.5.5
from ip_address import get_geographical_information, get_client_ip

try:
    from wsgiref.util import FileWrapper
except ImportError:
    from django.core.servers.basehttp import FileWrapper

from django.forms.models import model_to_dict
from django.http import JsonResponse
from web.models import Download, Acknowledgement, Bundle
from report_protocols.models import Package


# noinspection PyUnusedLocal
def home(request):
    # Get the packages
    return render_to_response('home/index.html')


# noinspection PyUnusedLocal
def biologists(request):
    context = {}

    # Get the packages
    packages = Package.objects.all()
    context['packages'] = packages
    return render_to_response('home/biologists.html', context)


# noinspection PyUnusedLocal
def facilities(request):

    return render_to_response('home/facilities.html')


# noinspection PyUnusedLocal
def developers(request):

    return render_to_response('home/developers.html')

def contact(request):

    packages = Package.objects.order_by("name")

    context = {
        "packages": packages,
    }
    return render_to_response('home/contactus.html', context)


def download_form(request):
    bundles = list(Bundle.objects.order_by('-version'))

    context = {
        "downloadables": bundles,
    }
    return render_to_response('home/download_form.html', context)


def utc_to_local(utc_dt):
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    return local_dt.replace(microsecond=utc_dt.microsecond)


def startDownload(request):
    bundleId = request.GET.get('bundleId')

    errors = ""
    bundle = None
    if not len(bundleId) > 0:
        errors += "File not specified.\n"
    else:
        # Get the bundle
        bundle = Bundle.objects.get(id=bundleId)

        if bundle is None:
            errors += "File with %s id not found." % bundleId

    if len(errors) == 0:

        # Get the ip
        client_ip = get_client_ip(request)
        # Get the country...
        country, city = get_geographical_information(client_ip)
        client_address = socket.getfqdn(client_ip)
        newDownload = Download.objects.create(
            country=country,
            version=bundle.version,
            platform=bundle.platform,
            size=bundle.size,
            city=city,
            ip=client_ip,
            client_address=client_address
        )

        # Return a response with the scipion download file
        path = bundle.file.file.name

        if not os.path.exists(path):
            return HttpResponseNotFound('Path not found: %s' % path)

        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(),
                                    content_type="application/tar+gzip")
            response['Content-Disposition'] = 'inline; filename=' \
                                              + os.path.basename(path)
            return response

    else:
        redirect(download_form)


# noinspection PyUnusedLocal
def getDownloadsStats(request):
    jsonStr = getDownloadsStatsToJSON()

    return HttpResponse(jsonStr, content_type='application/json')


def getDownloadsStatsToJSON():
    result = []
    for download in Download.objects.all():
        ddict = model_to_dict(download)
        ddict['timeStamp'] = utc_to_local(download.creation).isoformat()
        result.append(ddict)
    jsonStr = json.dumps(result, ensure_ascii=False)
    return jsonStr


# noinspection PyUnusedLocal
def showDownloadStats(request):
    context = {
        "downloadsJSON": getDownloadsStatsToJSON(),
    }
    return render_to_response('home/download_stats.html', context)


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
    return render_to_response('home/acknowledgements.html', context_dict)
