from __future__ import unicode_literals

from django.db import models
import datetime

# project assumes hash computed with hashlib.sha256()
from webservices import settings


class Package(models.Model):
    name = models.CharField(max_length=128, unique=True)
    # We add fields for pluginization
    pipName = models.CharField(max_length=256, help_text='Name of the plugin at pypi.org',
                               blank=True, default="")

    description = models.CharField(max_length=256, blank=True, default="")
    url = models.CharField(max_length=256, help_text="Software site url",
                           blank=True, default="")
    logo = models.ImageField(blank=True, upload_to=settings.PATH_PACKAGES)

    def __str__(self):  # For Python 2, use __unicode__ too
        return "package=%s,pipName=%s" % (self.name, self.pipName)


class ProtocolType(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256, default="")
    icon = models.ImageField(blank=True, upload_to=settings.PATH_PROT_TYPES)
    def __str__(self):  # For Python 2, use __unicode__ too
        return "Protocol type=%s"%(self.name)


class Protocol(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=2048,
                                   blank=True,
                                   null=True)
    timesUsed = models.IntegerField(default=0)
    package = models.ForeignKey(Package,
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE)
    protocolType = models.ForeignKey(ProtocolType,
                                     null=True,
                                     blank=True,
                                     on_delete=models.CASCADE)
    friendlyName = models.CharField(max_length=256, blank=True, null=True)
    def __str__(self):  # For Python 2, use __unicode__ too
        return "prot=%s, used=%d"%(self.name, self.timesUsed)

class IpAddressBlackList(models.Model):
    client_ip = models.GenericIPAddressField(null=True, unique=True)
    note = models.CharField(max_length=128, null=True)

    def __str__(self):
        return str(self.client_ip)

class Workflow(models.Model):
    project_uuid = models.CharField(max_length=44)
    project_workflow = models.TextField(null=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    lastModificationDate = models.DateTimeField(default=datetime.datetime.now)
    client_ip = models.GenericIPAddressField(null=True)
    client_address = models.CharField(max_length=256, null=True)
    client_country = models.CharField(max_length=256, null=True)
    client_city = models.CharField(max_length=256, null=True)
    timesModified = models.IntegerField(default=0)

    def __str__(self):  # For Python 2, use __unicode__ too
        return "workflow=%s, json=%s" % (self.project_uuid[:8], self.project_workflow)
