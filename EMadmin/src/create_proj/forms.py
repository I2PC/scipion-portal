from django import forms
from create_proj.models import Acquisition, Acquisition2
from fields import ListTextWidget
import os
from django.conf import settings
import subprocess
import re

class AcquisitionForm(forms.ModelForm):
    backupPath = forms.CharField(required=True, initial=settings.BACKUPMESSAGE)

    def __init__(self, *args, **kwargs):
        _dir_list = [os.path.join(settings.BACKUPPATH, o)
                     for o in os.listdir(settings.BACKUPPATH)
                     if os.path.isdir(os.path.join(settings.BACKUPPATH,o))]
        super(AcquisitionForm, self).__init__(*args, **kwargs)
        self.fields['backupPath'].widget = ListTextWidget(
                data_list=_dir_list, name='dir-list', size=40)

    def clean_backupPath(self):
        def is_running(process):
            counter = 0
            s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
            for x in s.stdout:
                if re.search(process, x):
                    counter = x.split()[0]
                    break
            return counter
        # if  lsyncd running report error TRANSFERTOOL
        counter = is_running(settings.TRANSFERTOOL)
        if counter > 0:
            msg = "There is a backup script running in the background " \
                  "I cannot continue unless you stop it. " \
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
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Acquisition2
        #fields = ('pixelsize','dose')
        exclude = ('acquisition',)
