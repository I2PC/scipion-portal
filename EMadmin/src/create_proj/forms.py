from django import forms
from create_proj.models import Microscope, Acquisition, PIXELSIZE_CHOICES
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

class AcquisitionForm(forms.ModelForm):
    #microscope = forms.ModelChoiceField(
    #        queryset=Microscope.objects.all(),
    #        help_text="Select Microscope")
    # user = forms.ModelChoiceField()
    #voltage = forms.FloatField(help_text="Voltage",initial=300)
    #sample = forms.CharField(help_text="Sample")
    #date = forms.DateTimeField(widget=forms.HiddenInput())
    #dose = forms.FloatField(help_text="Dose")
    #pixelsize = forms.FloatField(help_text="Pixel Size",
    #                             choices=PIXELSIZE_CHOICES,
    #                        initial=3.)
    #user = forms.CharField(widget=forms.HiddenInput())
    backupPath = forms.FileField(widget = forms.FileInput())
    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Acquisition
        fields = ('microscope','workflow', 'voltage',
                  'sample', 'date', 'backupPath')
