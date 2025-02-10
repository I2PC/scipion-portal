from __future__ import unicode_literals
import logging
logger = logging.getLogger(__name__)

import json
from collections import Counter

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

    project_uuid = models.CharField(max_length=44, null=True)
    project_workflow = models.TextField(null=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    lastModificationDate = models.DateTimeField(default=datetime.datetime.now)
    timesModified = models.IntegerField(default=0)
    prot_count = models.IntegerField(default=0)
    scipion_version = models.CharField(max_length=20, default="2.0")
    installation = models.ForeignKey(Installation, null=True, on_delete=models.CASCADE)

    def _countProtocols(self, workflow):

        try:
            return len(workflow.split(","))
        except Exception as e:
            return 0

    def getProtocolsCountDif(self, jsonList=None):
        """ Returns the difference in protocol counts ina Counter dictionary:
            {"Prot1":1, "Prot2":-3,...}
        """

        # Get its current json workflow
        existingCount = self.getProtCount(self.project_workflow)

        if not jsonList:

            return  existingCount
        # If json is passed we assume its an update, so we compute the difference
        else:

            newCount = self.getProtCount(jsonList)

            # logCounter("New count: ", newCount)
            # logCounter("Existing count: ", existingCount)

            newCount.subtract(existingCount)

            return newCount

    def getProtCount(self, jsonList):
        """ Returns a Counter (dict like) list with all the protocols and the amount of them in the workflow"""

        if jsonList is None or jsonList == "[]":
            return Counter()
        else:
            logger.info("Getting prot count for %s" % jsonList)
            return Counter([x.encode('latin-1') for x in json.loads(jsonList)])

    def save(self, *args, **kwargs):

        # Normalize empty projects
        if self.project_workflow == "[]" or self.project_workflow is None:
            self.project_workflow = None
            self.prot_count=0
        else:
            self.prot_count = self._countProtocols(self.project_workflow)

        super(Workflow, self).save()

    def __str__(self):  # For Python 2, use __unicode__ too
        return "uuid=%s, lmd=%s, prot_count=%s" % (self.project_uuid, self.lastModificationDate, self.prot_count)
