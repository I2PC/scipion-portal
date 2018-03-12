from django.forms import ModelForm, TextInput, Textarea
from models import Plugin


class PluginForm(ModelForm):
    class Meta:
        model = Plugin
        fields = ['name', 'dirName', 'pipName',
                  'pluginSourceUrl', 'binaryVersions', 'pluginVersions']
        widgets = {
            'name': TextInput(attrs={'placeholder': 'e.g. eman'}),
            'dirName': TextInput(attrs={'placeholder': 'e.g. eman2'}),
            'pipName': TextInput(attrs={'placeholder': 'e.g. scipion_eman'}),
            'pluginSourceUrl': TextInput(attrs={'placeholder': 'e.g. https://github.com/yaizar/scipion_eman',
                                                'size': 40}),
            'pluginVersions': Textarea(attrs={'value': None,
                                              'placeholder': 'Compatibility dict bw plugin and scipion E.g.:'
                                                              '\n{\n\t"1.0": ["1.2"],\n\t"1.1": ["1.2"],\n\t'
                                                              '"2.0": ["1.2","1.3"]\n}'}),
            'binaryVersions': TextInput(attrs={'placeholder': 'e.g: 2.11, 2,12'}),
        }