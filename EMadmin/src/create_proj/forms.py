from django import forms
from create_proj.models import Acquisition, Acquisition2
from fields import ListTextWidget
import os
from django.conf import settings
import subprocess
import re
from models import Acquisition
from datetime import datetime, timedelta
import psutil

class SkipAcquisitionForm(forms.Form):
    def __init__(self, *args, **kwargs):
         """Get projects done last week by current user"""
         user = kwargs.pop('user',None)
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
        self.request = kwargs.pop('request',None)
        _dir_list = [os.path.join(settings.BACKUPPATH, o)
                     for o in os.listdir(settings.BACKUPPATH)
                     if os.path.isdir(os.path.join(settings.BACKUPPATH,o))]
        super(AcquisitionForm, self).__init__(*args, **kwargs)
        self.fields['backupPath'].widget = ListTextWidget(
                data_list=_dir_list, name='dir-list', size=40)

    def clean_backupPath(self):
        def is_running(process):
            from subprocess import check_output
            try:
                pidList = check_output(["pidof",process])
            except subprocess.CalledProcessError:
                pidList = [0]
            return pidList

        # if  lsyncd running report error TRANSFERTOOL
        counterList = is_running(settings.TRANSFERTOOL)
        if len(counterList) > 0 and\
                (not self.cleaned_data['multiple_backup']):
            msg = "There are %d backup scripts (%s) running in the background " \
                  "Consider killing Them. Execute in a terminal: " \
                  "'ps -ef | grep %s' to get a list with the  processes." \
                  "Use 'kill -9 process_number' to kill the process. " \
                  "If you want to ignore this warning just resend the form" %\
                  (len(counterList), settings.TRANSFERTOOL, settings.TRANSFERTOOL)
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
