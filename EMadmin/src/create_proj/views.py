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
from parse_protocol import parse_protocol
import subprocess

@login_required
def index(request):
    return HttpResponse("Rango says hey there world!")

def create_directory_three(acquisition):
    """ Create directories to store movies
    """
    def _createPath(p):
        # Create the project path
        if not os.path.exists(p):
            os.makedirs(p)

    # get root directory
    dataPath = acquisition.microscope.dataFolder
    projname = acquisition.projname
    projPath = os.path.join(dataPath,projname)
    sys.stdout.write("Creating directories at path '%s' ... " % projPath)
    _createPath(projPath)

    #create GRIDS
    for i in range(12):
        gridFolder = os.path.join(projPath, 'GRID_%02d' % (i + 1))
        _createPath(os.path.join(gridFolder, 'ATLAS'))
        _createPath(os.path.join(gridFolder, 'DATA'))

def launch_backup(acquisition):
    """backup using lsyncd
    """
    print "launch_backup"
    if acquisition.backupPath == settings.BACKUPMESSAGE:
        return
    else:
        print "launch_backup1"
        # get root directory
        scipion_user_data = settings.SCIPIONUSERDATA
        projname = acquisition.projname
        sourcePath = os.path.join(scipion_user_data, 'projects', projname)
        print "scipion_user_data",scipion_user_data
        print "projname", projname
        args = settings.TRANSFERTOOLARGS
        print "args1",  args
        args += [sourcePath]
        print "args2",  args
        args += [acquisition.backupPath]
        print "args3",  args
        print [settings.TRANSFERTOOL] +  args
        print "args4",  args
        s = subprocess.Popen([settings.TRANSFERTOOL] +  args)
        print "launch_backup2"

@login_required
def add_acquisition(request):
    """
    Show first half of the form that is parameters that
    can be set before the microscope is acquiring data
    """
    if request.method == 'POST':
        form = AcquisitionForm(request.POST)
        if form.is_valid():
            try:
                acquisition = form.save(commit=False)
                acquisition.user = request.user  # set logged user
                acquisition.save()
            except IntegrityError as e:
                # check if the project already exsits
                if 'UNIQUE' in e.args[0]:
                    form.errors['sample'] = ["Exists a project with this " \
                                            "name: %s." % acquisition.projname,
                                             "Please change Sample field"]
                    return render(request,
                              'create_proj/add_acquisition.html',
                              {'form': form})
                else:
                    form.errors['microscope'] = e.args[0]
            # save acquisition as session variable so we can link
            # it with acquisition2
            request.session['idacquisition'] = acquisition.id
            # create directories for data (in mic storage disk)
            create_directory_three(acquisition)
            # show second part of the form
            return redirect(reverse('create_proj:add_acquisition2'))
    else:
        form = AcquisitionForm()  # create a clean form
    return render(request,
                  'create_proj/add_acquisition.html',
                  {'form': form})

def save_workflow(acquisition2):
    """
    Get workflow from database
    """
    acquisition = acquisition2.acquisition
    # get root directory
    dataPath = acquisition.microscope.dataFolder
    projname = acquisition.projname
    projectPath = os.path.join(dataPath, projname)
    workflow = acquisition.workflow.workflow
    workflowPath = os.path.join(projectPath, settings.WORKFLOWFILENAME)
    # PARSE PROTOCOLS
    #  convert protocol to dictionary
    parseWorkFlow  = json.loads(workflow)
    # modify fields
    for protocol in parseWorkFlow:
        parse_protocol(protocol, acquisition2)
    # convert dictionary back to json
    workflow = json.dumps(parseWorkFlow)
    # save workflow
    f = open(workflowPath,'w')
    f.write(workflow)
    f.close()

def create_project(acquisition2):
    """create project from workflow file"""
    acquisition = acquisition2.acquisition
    # get root directory
    scipion = os.path.join(settings.SCIPIONPATH,'scipion')
    script = os.path.join(settings.SCIPIONPATH,'scripts/create_project.py')
    projname = acquisition.projname
    dataPath = acquisition.microscope.dataFolder
    workflowPath = os.path.join(dataPath,projname,settings.WORKFLOWFILENAME)
    #run command
    args = ["python"]
    args += [script]
    args += [projname]
    args += [workflowPath]
    proc = subprocess.Popen([scipion] +  args)
    proc.wait() # wait untill process finish

    #command = scipion + " python " + script + " " + projname + " " + \
    #          workflowPath
    #os.system(command)

def call_scipion_last(acquisition2):
    """ start scipion """

    print "call_scipion_last"
    # get root directory
    scipion = os.path.join(settings.SCIPIONPATH,'scipion')
    #run command
    args = ["last"]
    proc = subprocess.Popen([scipion] +  args)

def schedule_protocol(acquisition2):
    """
    :param acquisition2: if requested run python in schedule mode"
    :return:
    """
    acquisition = acquisition2.acquisition
    if acquisition.schedule is False:
        return
    # get root directory
    scipion = os.path.join(settings.SCIPIONPATH,'scipion')
    script = os.path.join(settings.SCIPIONPATH,'scripts/schedule_project.py')
    projname = acquisition.projname
    # dataPath = acquisition.microscope.dataFolder
    # workfowPath = os.path.join(dataPath,projname,settings.WORKFLOWFILENAME)
    # run command
    # command = scipion + " python " + script + " " + projname
    # os.system(command)

    args = ["python"]
    args += [script]
    args += [projname]
    proc = subprocess.Popen([scipion] +  args)
    proc.wait()


@login_required
def add_acquisition2(request):
    """ Process second half of the form
    """
    if request.method == 'POST':
        form = AcquisitionForm2(request.POST)
        if form.is_valid():
            acquisition2 = form.save(commit=False)
            # link to Acquisition object
            acquisition2.acquisition = \
                Acquisition.objects.get(pk=request.session['idacquisition'])
            acquisition2.save()
            #create workflow and replace values
            save_workflow(acquisition2)
            #create_project
            create_project(acquisition2)
            #schedule?
            schedule_protocol(acquisition2)
            #open scipion
            call_scipion_last(acquisition2)
            # launch backup
            launch_backup(acquisition2.acquisition)

        else:
            pass
        return render(request,'create_proj/done.html',{})
    else:
        form = AcquisitionForm2()
        return render(request,
                      'create_proj/add_acquisition2.html',
                      {'form': form})