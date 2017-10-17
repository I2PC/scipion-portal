from django import forms
from create_proj.models import Acquisition, Acquisition2
#from django.contrib.auth.models import User
#from django.contrib.auth import get_user_model
#User = get_user_model()

class AcquisitionForm(forms.ModelForm):
    ###backupPath = forms.FileField(widget = forms.FileInput())
    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Acquisition
#        fields = ('microscope','workflow', 'voltage',
#                  'sample', 'date','backupPath')
        exclude = ('user', 'projname')

class AcquisitionForm2(forms.ModelForm):
    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Acquisition2
        #fields = ('pixelsize','dose')
        exclude = ('acquisition',)
