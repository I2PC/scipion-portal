from __future__ import unicode_literals

from django.db import models
from report_protocols.models import Package

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

