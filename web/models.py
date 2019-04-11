from __future__ import unicode_literals

import uuid

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from report_protocols.models import Package
from webservices import settings


class Download(models.Model):

    class Meta:
        ordering = ('creation',)

    creation = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=256, null=True)
    city = models.CharField(max_length=256, null=True)
    ip = models.GenericIPAddressField(null=True)
    version = models.CharField(max_length=16)
    platform = models.CharField(max_length=256)
    size = models.CharField(max_length=256)

class Bundle(models.Model):
    file = models.FileField(upload_to=settings.PATH_BUNDLES)
    version = models.CharField(max_length=20)  # Bundle version
    platform = models.CharField(max_length=256)  # Type (sources/binaries)
    size = models.CharField(max_length=256)  # Bundle size
    date = models.DateTimeField(auto_now_add=True)  # Release date
    deprecated = models.BooleanField(default=False)


@python_2_unicode_compatible
class Acknowledgement(models.Model):

    class Meta:
        verbose_name = 'Contributor'
        verbose_name_plural = 'Contributors'

    title = models.CharField(max_length=256)
    description = models.CharField(max_length=500)
    url = models.CharField(max_length=500, null=True, blank=True)
    image = models.CharField(max_length=500, null=True, blank=True)
    githubName = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.title

class Contribution(models.Model):
    contributor = models.ForeignKey(Acknowledgement,
                                     null=False,
                                     blank=False,
                                     on_delete=models.CASCADE)
    package = models.ForeignKey(Package,
                                     null=False,
                                     blank=False,
                                     on_delete=models.CASCADE)

