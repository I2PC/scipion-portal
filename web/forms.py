from django.forms import ModelForm, TextInput
from models import Plugin


class PluginForm(ModelForm):
    class Meta:
        model = Plugin
        fields = ['name', 'pipName']
        widgets = {
            'pipName': TextInput(attrs={'placeholder': 'e.g. scipion_eman'}),
            'name': TextInput(attrs={'placeholder': 'e.g. eman'}),

        }