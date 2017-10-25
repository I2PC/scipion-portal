from django import forms
from create_proj.models import Acquisition, Acquisition2
from fields import ListTextWidget
import os
from django.conf import settings
import subprocess
import re
from models import Acquisition
from datetime import datetime, timedelta


class SkipAcquisitionForm(forms.Form):
    def __init__(self, *args, **kwargs):
         """Get projects done last week by current user"""
         user = kwargs.pop('user',None)
         print "user", user
         last_week = datetime.today() - timedelta(days=7)
         super(SkipAcquisitionForm, self).__init__(*args, **kwargs)
         self.fields['project'].queryset =  \
             Acquisition.objects.filter(date__gte=last_week,
                                        user=user).order_by('-date')

    """Show objects recorded last week"""
    project = forms.ModelChoiceField(queryset=None, initial=0)

class AcquisitionForm(forms.ModelForm):
    backupPath = forms.CharField(required=True,
                                 initial=settings.BACKUPMESSAGE)
    schedule = forms.BooleanField(initial=False,
                                  help_text="run scipion in batch mode",
                                  required=False)
    def __init__(self, *args, **kwargs):
        _dir_list = [os.path.join(settings.BACKUPPATH, o)
                     for o in os.listdir(settings.BACKUPPATH)
                     if os.path.isdir(os.path.join(settings.BACKUPPATH,o))]
        super(AcquisitionForm, self).__init__(*args, **kwargs)
        self.fields['backupPath'].widget = ListTextWidget(
                data_list=_dir_list, name='dir-list', size=40)

#    def clean_backupPath(self):
#        def is_running(process):
#            from subprocess import check_output
#            try:
#                pidList = check_output(["pidof",process])
#            except subprocess.CalledProcessError:
#                pidList = [0]
#            return pidList

    def find_procs_by_name(self,name):
        "Return a list of processes matching 'name'."
        assert name, name
        ls = []
        for p in psutil.process_iter():
            name_, exe, cmdline = "", "", []
            try:
                name_ = p.name()
                cmdline = p.cmdline()
                exe = p.exe()
            except (psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except psutil.NoSuchProcess:
                continue
            if name == name_ or cmdline[0] == name or os.path.basename(exe) == name:
                ls.append(name)
        return ls
        # if  lsyncd running report error TRANSFERTOOL
        counterList = is_running(settings.TRANSFERTOOL)
        if len(counterList) > 0:
            msg = "There are %d backup scripts running in the background " \
                  "Consider killing Them. " \
                  "The command 'kill -9 %s' will kill it. " \
                  "Execute it at your own risk from a terminal" % counter
            raise forms.ValidationError(msg)
        return self.cleaned_data.get('backupPath')
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Acquisition
#        fields = ('microscope','workflow', 'voltage',
#                  'sample', 'date','backupPath')
        exclude = ('user', 'projname', 'date')

class AcquisitionForm2(forms.ModelForm):
    # An inline class to provide additional information on the form.
    sampling_rate = forms.FloatField(label="Sampling rate (A/px)")
    illuminated_area = forms.FloatField(label="Illuminated area (m)")
    dose_per_frame = forms.FloatField(label="Dose per fraction (e/A^2)")
    dose_rate = forms.FloatField(label="Dose rate (e/(px*sec))")
    total_exposure_time = forms.FloatField(label="Total exposure time (sec)")
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Acquisition2
        #fields = ('pixelsize','dose')
        exclude = ('acquisition',)
