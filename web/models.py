from __future__ import unicode_literals
from django.db import models
from django.forms import ModelForm, TextInput
from django.contrib.postgres.fields import ArrayField, JSONField


class Download(models.Model):

    class Meta:
        ordering = ('creation',)

    creation = models.DateTimeField(auto_now_add=True)
    fullName = models.CharField(max_length=256)
    organization = models.CharField(max_length=256)
    email = models.CharField(max_length=256)
    subscription = models.BooleanField()
    country = models.CharField(max_length=256)
    version = models.CharField(max_length=16)
    platform = models.CharField(max_length=256)
    size = models.CharField(max_length=256)


class Acknowledgement(models.Model):

    title = models.CharField(max_length=256)
    description = models.CharField(max_length=500)
    url = models.CharField(max_length=500, null=True, blank=True)
    image = models.CharField(max_length=500, null=True, blank=True)


class Plugin(models.Model):

    name = models.CharField(max_length=256, help_text='name used to install')
    dirName = models.CharField(max_length=256,
                               help_text='name of folder in pip package')
    pipName = models.CharField(max_length=256, null=True, blank=True, )
    pluginSourceUrl = models.CharField(max_length=500, null=True, blank=True)
    binaryVersions = ArrayField(models.CharField(max_length=20))
    pluginVersions = JSONField(blank=True, null=True, default=None)




