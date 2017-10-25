# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from forms import AcquisitionForm, SkipAcquisitionForm, AcquisitionForm2
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

#ACQUISITION AUX FUNCTION
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
        print "create", gridFolder

def launch_backup(acquisition):
    """backup using lsyncd
    """

    if acquisition.backupPath == settings.BACKUPMESSAGE:
        return
    else:
        # get root directory
        scipion_user_data = settings.SCIPIONUSERDATA
        projname = acquisition.projname
        sourcePath = os.path.join(scipion_user_data, 'projects', projname)
        targetPath = os.path.join(acquisition.backupPath, projname)
        args = settings.TRANSFERTOOLARGS
        args += [sourcePath]
        args += [targetPath]
        print [settings.TRANSFERTOOL] +  args
        s = subprocess.Popen([settings.TRANSFERTOOL] +  args)

@login_required
def add_acquisition(request):
    """
    Show first half of the form that is parameters that
    can be set before the microscope is acquiring data
    """
    if request.method == 'POST':
        doNotSkip = False
        if u'skip_submit_add_acquisition' in request.POST:
            formP = SkipAcquisitionForm(data=request.POST, user=request.user)
        else:
            formP = AcquisitionForm(request.POST)
            doNotSkip = True
        if formP.is_valid():
            if doNotSkip:
                try:
                    acquisition = formP.save(commit=False)
                    acquisition.user = request.user  # set logged user
                    acquisition.save()
                except IntegrityError as e:
                    # check if the project already exsits
                    if 'UNIQUE' in e.args[0]:
                        formP.errors['sample'] = ["Exists a project with this " \
                                                "name: %s." % acquisition.projname,
                                                 "Please change Sample field"]
                        return render(request,
                                  'create_proj/add_acquisition.html',
                                  {'form': formP})
                    else:
                        formP.errors['microscope'] = e.args[0]
                # create directories for data (in mic storage disk)
                create_directory_three(acquisition)
            else:
                acquisition =formP.cleaned_data['project']
            # save acquisition as session variable so we can link
            # it with acquisition2
            request.session['idacquisition'] = acquisition.id
            # show second part of the form
            return redirect(reverse('create_proj:add_acquisition2'))
        else:
            print "HORROR: what am I doing here? add_acquisition"
    else:
        form = AcquisitionForm()  # create a clean form
        form2 = SkipAcquisitionForm(user=request.user)  # create a clean form
    return render(request,
                  'create_proj/add_acquisition.html',
                  {'form': form, 'form2': form2})

# AUX FUNCTION FOR ACQUISITION2
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
    print "CREATE WORKFLOW", workflowPath

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
    print scipion, args
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
            try:
                acquisition2 = form.save(commit=False)
                # link to Acquisition object
                acquisition2.acquisition = \
                    Acquisition.objects.get(pk=request.session['idacquisition'])
                acquisition2.save()
            except IntegrityError as e:
                # check if the project already exsits
                if 'UNIQUE' in e.args[0]:
                    form.errors['nominal_magnification'] = ["Exists a project with this " \
                                             "name: %s." % acquisition2.acquisition.projname,
                                             "Please create a totally new project"]
                    return render(request,
                                  'create_proj/add_acquisition2.html',
                                  {'form': form})

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
        _dict = {}
        projname = acquisition2.acquisition.projname
        username = settings.PUBLISHUSER
        _url = settings.PUBLISHURL
        _dict["URL"]="http://%s/%s/%s"%(_url, username, projname)
        return render(request,'create_proj/done.html',_dict)
    else:
        form = AcquisitionForm2()
        return render(request,
                      'create_proj/add_acquisition2.html',
                      {'form': form})

