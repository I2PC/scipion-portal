# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.http import HttpResponse
from forms import AcquisitionForm
from models import Microscope
import os, sys
import pyworkflow.utils as pwutils

@login_required
def index(request):
    return HttpResponse("Rango says hey there world!")

@login_required
def create_directory_three(acquisition):
    def _createPath(p):
        # Create the project path
        sys.stdout.write("Creating path '%s' ... " % p)
        pwutils.makePath(p)
        sys.stdout.write("DONE\n")

    # get root directory
    dataPath = acquisition.microscope.dataFolder
    projname = acquisition.projname
    projPath = os.path.join(dataPath,projname)
    _createPath(projPath)

    #create GRIDS
    for i in range(12):
        gridFolder = os.path.join(projPath, 'GRID_%02d' % (i + 1))
        _createPath(os.path.join(gridFolder, 'ATLAS'))
        _createPath(os.path.join(gridFolder, 'DATA'))
    #_createPath(scipionProjPath)
    # get workflow and pass it to scipion
    # back up

@login_required
def add_acquisition(request):
    if request.method == 'POST':
        form = AcquisitionForm(request.POST)
        if form.is_valid():
            acquisition = form.save(commit=False)
            acquisition.user = request.user
            acquisition.save()
            create_directory_three(acquisition)
        else:
            pass

        return HttpResponse("Jump to Scipion page")
    else:
        form = AcquisitionForm()
        return render(request,
                      'create_proj/add_acquisition.html',
                      {'form': form})