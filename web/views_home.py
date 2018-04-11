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
from datetime import datetime, timedelta, tzinfo
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.template.context_processors import csrf
# Depending on DJANGO version (first is for DJANGO 1.9) second for 1.5.5
try:
    from wsgiref.util import FileWrapper
except ImportError:
    from django.core.servers.basehttp import FileWrapper

from web.email import validateEmail, subscribeToUsersList
import mimetypes

from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.conf import settings
from django.core import serializers
from web.models import Download, Acknowledgement, Plugin

FILE_TO_DOWNLOAD = 'fileToDownload'

DOWNLOADABLES_FILE = 'file'

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

def home(request):
    context = {
        "abs_url": getAbsoluteURL(),
    }
    return render_to_response('home/index.html', context)

def download_form(request):
    # Load the downloadables data
    downloadables = loadDownloadables()

    context = {
        "downloadables": downloadables,
        "abs_url": getAbsoluteURL(),
    }
    context.update(csrf(request))
    return render_to_response('home/download_form.2.html', context)

def utc_to_local(utc_dt):
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    return local_dt.replace(microsecond=utc_dt.microsecond)

def getAbsoluteURL(additionalPath=None):
    if additionalPath is None:
        additionalPath = ''
    return '/' + additionalPath

def loadDownloadables():
    f = open(getInstallPath("downloadables.json"))

    d = json.load(f)

    f.close()

    checkDowloadablesExistence(d)

    return d


def checkDowloadablesExistence(downloadables):
    """ Structure should be like this:

    Parameters
    ----------
    downloadables: list of downloadable files

    """

    for version, files in downloadables.iteritems():
        # remove all files that doesn't exists
        files[:] = [dFile for dFile in files if os.path.exists(getInstallPath(dFile.get(DOWNLOADABLES_FILE)))]


def getInstallPath(fileName=''):
    return os.path.join(SCRIPT_DIRECTORY, "../static/install", fileName)


def startDownload(request):
    fullName = request.POST.get('fullName')
    organization = request.POST.get('organization')
    email = request.POST.get('email')
    mailoption = request.POST.get('mailoption')
    country = request.POST.get('country')
    bundle = request.POST.get('file')

    errors = ""

    # If full name is None it's a direct access..
    if fullName is None:
        return redirect('download_form')

    if not len(fullName) > 0:
        errors += "Please fill in the fullName field.\n"
    if not len(organization) > 0:
        errors += "Please fill in the Organization field.\n"
    if not len(email) > 0 and validateEmail(email):
        errors += "Please fill in the Email field.\n"
    # if not len(mailoption) > 0:
    #         errors += "Please choose one into the Country field.\n"
    if not len(bundle) > 0:
        errors += "Please fill in the Scipion Version field.\n"

    if len(errors) == 0:

        fileSplit = bundle.split("~")
        version = fileSplit[0]
        platform = fileSplit[1]
        fileName = fileSplit[2]
        size = fileSplit[3]

        download = Download.objects.create(
            fullName=fullName,
            organization=organization,
            email=email,
            subscription=mailoption == "0",
            country=country,
            version=version,
            platform=platform,
            size=size
        )

        # If the user want's to be subscribed
        if mailoption == '0': subscribeToUsersList(email)

        # Return a response with the scipion download file
        path = getInstallPath(fileName)

        if not os.path.exists(path):
            return HttpResponseNotFound('Path not found: %s' % path)

        request.session[FILE_TO_DOWNLOAD] = fileName

        context = {
            "fileToDownload": fileName,
            "abs_url": getAbsoluteURL(),
        }
        context.update(csrf(request))

        return render_to_response('home/startdownload.html', context)

    else:
        redirect(download_form)

def doDownload(request):

    # Return a response with the scipion download file
    if FILE_TO_DOWNLOAD in request.session:

        fileToDownload = request.session[FILE_TO_DOWNLOAD]

        path = getInstallPath(fileToDownload)

        if not os.path.exists(path):
            return HttpResponseNotFound('Path not found: %s' % path)

        response = HttpResponse(FileWrapper(open(path)),
                                content_type=mimetypes.guess_type(path)[0])
        response['Content-Length'] = os.path.getsize(path)
        response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(path)

        return response
    else:

        return redirect('download_form')


def getDownloadsStats(request):

    jsonStr = getDownloadsStatsToJSON()

    return HttpResponse(jsonStr, content_type='application/json')


def getDownloadsStatsToJSON():
    result = []
    for download in Download.objects.all():
        ddict = model_to_dict(download)
        del ddict['email']
        del ddict['fullName']
        #from pdb import set_trace; set_trace()
        ddict['timeStamp'] = utc_to_local(download.creation).isoformat()

        # Convert subscription: 0 = Yes 1 = No
        ddict['subscription'] = ('Yes' if ddict['subscription'] else 'No')
        result.append(ddict)
    jsonStr = json.dumps(result, ensure_ascii=False)
    return jsonStr


def showDownloadStats(request):
    context = {
        "downloadsJSON": getDownloadsStatsToJSON(),
        "abs_url": getAbsoluteURL(),
    }
    return render_to_response('home/download_stats.html', context)

def getPluginsDict():
    result = {}
    for plugin in Plugin.objects.all():
        pluginDict = model_to_dict(plugin)
        result[pluginDict['pipName']] = pluginDict
    return result

def getPluginsJSON(request):
    return JsonResponse(getPluginsDict(), json_dumps_params={'indent': 4})


def acknowledgements(request):
    acknowledgements = Acknowledgement.objects.all()
    context_dict = {}
    context_dict['acknowledgements'] = acknowledgements
    return render_to_response('home/acknowledgements.html', context_dict)