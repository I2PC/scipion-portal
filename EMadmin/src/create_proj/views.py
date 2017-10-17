# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from forms import AcquisitionForm, AcquisitionForm2
from models import Acquisition
import os, sys
from django.shortcuts import redirect
from django.conf import settings
from django.db import IntegrityError
import json

@login_required
def index(request):
    return HttpResponse("Rango says hey there world!")

@login_required
def create_directory_three(acquisition):
    def _createPath(p):
        # Create the project path
        sys.stdout.write("Creating path '%s' ... " % p)
        if not os.path.exists(p):
            os.makedirs(p)
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
            try:
                acquisition = form.save(commit=False)
                acquisition.user = request.user
                acquisition.save()
            except IntegrityError as e:
                if 'UNIQUE' in e.args[0]:
                    return HttpResponse("Exists a project with this name. "
                                        "Please provide a different one. Project name=%s"%acquisition.projname)
                else:
                    print "args", e
            request.session['idacquisition'] = acquisition.id
            create_directory_three(acquisition)
            return redirect(reverse('create_proj:add_acquisition2'))
        else:
            return HttpResponse("ERROR in add_acquisition:-(")
    else:
        form = AcquisitionForm()
        return render(request,
                      'create_proj/add_acquisition.html',
                      {'form': form})

def save_workflow(acquisition2):
    acquisition = acquisition2.acquisition
    # get root directory
    dataPath = acquisition.microscope.dataFolder
    projname = acquisition.projname
    projectPath = os.path.join(dataPath, projname)
    workflow = acquisition.workflow.workflow
    workflowPath = os.path.join(projectPath, settings.WORKFLOWFILENAME)
    #parse workflow
    parseWorkFlow  = json.loads(workflow)
    ###Make modules for each workflow
    #import
    #centralizate this string
    parseWorkFlow[0]['filesPath'] = projectPath + '/GRID_??/DATA/Images-Disc1/GridSquare_*/Data/'
    #modify workflow
    workflow = json.dumps(parseWorkFlow)
    #save workflow
    f = open(workflowPath,'w')
    f.write(workflow)
    f.close()
    #some editing is needed here to change the workflow

def create_project(acquisition2):
    """./../ scipion_box / scipion
    python.. /../ scipion_box / scripts / create_project.py
    kk / home / scipionuser / OffloadData / * / * json
    """
    acquisition = acquisition2.acquisition
    # get root directory
    scipion = os.path.join(settings.SCIPIONPATH,'scipion')
    script = os.path.join(settings.SCIPIONPATH,'scripts/create_project.py')
    projname = acquisition.projname
    dataPath = acquisition.microscope.dataFolder
    workfowPath = os.path.join(dataPath,projname,settings.WORKFLOWFILENAME)
    #run command
    command = scipion + " python " + script + " " + projname + " " + workfowPath
    os.system(command)

@login_required
def add_acquisition2(request):
    if request.method == 'POST':
        form = AcquisitionForm2(request.POST)
        if form.is_valid():
            acquisition2 = form.save(commit=False)
            print "acquisition", request.session['idacquisition']
            acquisition2.acquisition = Acquisition.objects.get(pk=request.session['idacquisition'])
            acquisition2.save()
            #save workflow
            save_workflow(acquisition2)
            #create_project
            create_project(acquisition2)
            #open scipion

        else:
            pass

        return HttpResponse("Acquisition2 done")
    else:
        form = AcquisitionForm2()
        return render(request,
                      'create_proj/add_acquisition2.html',
                      {'form': form})