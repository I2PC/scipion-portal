from __future__ import unicode_literals

from django.db import models
import datetime

# project assumes hash computed with hashlib.sha256()

class Protocol(models.Model):
    name = models.CharField(max_length=44)
    package = models.CharField(max_length=44, null=True)
    timesUsed = models.IntegerField(default=0)
    def __str__(self):  # For Python 2, use __unicode__ too
        return "prot=%s, used=%d"%(self.name, self.timesUsed)

class Workflow(models.Model):
    project_uuid = models.CharField(max_length=44)
    project_workflow = models.TextField(null=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    client_ip = models.GenericIPAddressField(null=True)

    def __str__(self):  # For Python 2, use __unicode__ too
        return "workflow=%s, json=%s"%(self.hash[:8],self.json)
