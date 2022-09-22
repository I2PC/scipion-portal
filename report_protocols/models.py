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
        return self.name


class ProtocolType(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256, default="")
    icon = models.ImageField(blank=True, upload_to=settings.PATH_PROT_TYPES)
    def __str__(self):  # For Python 2, use __unicode__ too
        return self.name

    @property
    def sorted_protocol_set(self):
        return self.protocol_set.order_by('friendlyName')

class Protocol(models.Model):

    class Meta:
        ordering = ['friendlyName', 'name']

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
        return "%s (%s)" % (self.name, self.friendlyName)

class IpAddressBlackList(models.Model):
    client_ip = models.GenericIPAddressField(null=True, unique=True)
    note = models.CharField(max_length=128, null=True)

    def __str__(self):
        return str(self.client_ip)


class Installation(models.Model):
    """ Class to hold information about Scipion installations"""
    creation_date = models.DateTimeField(default=datetime.datetime.now)
    lastSeen = models.DateTimeField(default=datetime.datetime.now)
    client_ip = models.GenericIPAddressField(null=True)
    client_address = models.CharField(max_length=256, null=True)
    client_country = models.CharField(max_length=256, null=True)
    client_city = models.CharField(max_length=256, null=True)
    scipion_version = models.CharField(max_length=20, default="2.0")

    def __str__(self):
        return "%s (%s)" % (self.client_ip, self.client_country)
class Workflow(models.Model):

    project_uuid = models.CharField(max_length=44)
    project_workflow = models.TextField(null=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    lastModificationDate = models.DateTimeField(default=datetime.datetime.now)
    timesModified = models.IntegerField(default=0)
    prot_count = models.IntegerField(default=0)
    scipion_version = models.CharField(max_length=20, default="2.0")
    installation = models.ForeignKey(Installation, null=True, on_delete=models.CASCADE)

    def _countProtocols(self, workflow):

        try:
            if workflow == "[]":
                return 0
            else:
                return len(workflow.split(","))
        except Exception as e:
            return 0

    def save(self, *args, **kwargs):

        self.prot_count = self._countProtocols(self.project_workflow)
        super(Workflow, self).save()

    def __str__(self):  # For Python 2, use __unicode__ too
        return "address=%s, lmd=%s, prot_count=%s" % (self.installation.client_address, self.lastModificationDate, self.prot_count)
