from __future__ import unicode_literals
import logging

logger = logging.getLogger(__name__)

import json
from collections import Counter

from django.db import models
import datetime
from django.utils import timezone

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

    @classmethod
    def reset_prot_count(cls):

        for prot in Protocol.objects.all():
            prot.timesUsed = 0
            prot.save()
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

    @property
    def months_dead(self):
        """months since the installation hasn't reported anything"""
        today = timezone.now().date()
        diff = today - self.lastSeen.date()

        return int(diff.days / 30.44)

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
            sw = ScipionWorkflow(jsonStr=workflow)
            return sw.getCount()
        except Exception as e:
            return 0

    def getProtocolsCountDiff(self, jsonList=None):
        """ Returns the difference in protocol counts in a Counter dictionary:
            {"Prot1":1, "Prot2":-3,...}
        """

        # Get its current json workflow
        existingCount, existingNextProtCount = self.getProtCount(self.project_workflow)

        if not jsonList:

            return existingCount, existingNextProtCount
        # If json is passed we assume its an update, so we compute the difference
        else:

            newCount, newNextProtCount = self.getProtCount(jsonList)
            newCount.subtract(existingCount)
            newNextProtCount.subtract(existingNextProtCount)

            return newCount, newNextProtCount

    def getProtCount(self, jsonList):
        """ Returns 2 Counter (dict like) list with
          1.- all the protocols and the amount of them in the workflow.
          2.- the "next protocol" count."""

        if self.isEmpty(jsonStr=jsonList):
            return Counter(), Counter()
        else:
            logger.info("Getting prot count for %s" % jsonList)
            sw = ScipionWorkflow(jsonStr=jsonList)
            protCounter = Counter()
            nextProtCounter = Counter()
            for prot, protStat in sw.getProtStats().items():
                protCounter.update({prot: protStat.getCount()})
                for nextProtName, count in protStat._nextProts.items():
                    nextProtKey = self.getNextProtocolKey(prot,nextProtName)
                    nextProtCounter.update({nextProtKey: count})

            return protCounter, nextProtCounter

    def saveProtCount(self, countDiff):
        for protocolName, numberTimes in countDiff.items():
            if Protocol.objects.filter(name=protocolName).exists():
                protocolObj = Protocol.objects.get(name=protocolName)
            else:
                protocolObj = Protocol(name=protocolName)
            protocolObj.timesUsed += numberTimes
            protocolObj.save()

    def getNextProtocolKey(self, mainProt, nextProt):
        return mainProt + "-" + nextProt

    def getProtsFromNextProtKey(self, nextProtKey):
        return nextProtKey.split("-")
    def saveNextProtCount(self, countDiff):

        for nextProtocolKey, numberTimes in countDiff.items():

            mainProtName, nextProtName = self.getProtsFromNextProtKey(nextProtocolKey)

            filter = {"protocol__name":mainProtName, "next_protocol__name":nextProtName}

            try:
                nextProts = NextProtocol.objects.get(**filter)
            except Exception as e:

                # Populate with the protocols
                prot = Protocol.objects.get(name=mainProtName)
                nextProt = Protocol.objects.get(name=nextProtName)
                nextProts = NextProtocol.objects.create(protocol=prot, next_protocol=nextProt)


            nextProts.count += numberTimes
            nextProts.save()

    def save(self, *args, **kwargs):

        # Normalize empty projects
        if self.isEmpty():
            self.project_workflow = None
            self.prot_count=0
        else:
            self.prot_count = self._countProtocols(self.project_workflow)

        super(Workflow, self).save()

    def isEmpty(self, jsonStr=None):

        if jsonStr is None:
            jsonStr = self.project_workflow

        return jsonStr in ["[]", "{}"] or jsonStr is None

    def __str__(self):  # For Python 2, use __unicode__ too
        return "uuid=%s, lmd=%s, prot_count=%s" % (self.project_uuid, self.lastModificationDate, self.prot_count)


class NextProtocol(models.Model):

    protocol = models.ForeignKey(Protocol, null=False, on_delete=models.CASCADE, related_name="main_protocol")  # Main protocol
    next_protocol = models.ForeignKey(Protocol, null=False, on_delete=models.CASCADE, related_name="next_protocol")  # Next protocol after main
    count = models.IntegerField(default=0)  # How many times"next_protocol is being used after protocol.


class ProtStat:
    """ Class to store the usage part of a reported ScipionWorkflow"""
    def __init__(self, count=0, nextProtsDict=None):
        self._count = count
        self._nextProts = nextProtsDict or dict()

    def getCount(self):
        return self._count
    def addUsage(self, count=1):
        self._count += count
    def addCountToNextProtocol(self, nextProt, count=1):
        self._nextProts[nextProt] = self._nextProts.get(nextProt, 0) + count

    def toJSON(self):
        str = "[%s,{%s}]"
        nextProtS = ""

        if len(self._nextProts):
            nextProtA = []
            for protName, count in self._nextProts.items():
                nextProtA.append('"%s":%d' % (protName, count))

            nextProtS= ",".join(nextProtA)

        str = str % (self._count, nextProtS)

        return str

    def __repr__(self):
        return self.toJSON()

class ScipionWorkflow:
    """ Class to serialize and deserialize what is reported from scipion.
    Example: {"ProtA":
                [2, {
                        "ProtB":2,
                        "ProtC":3,
                        ...
                    }
                ], ...
              }
    """

    def __init__(self, jsonStr=None):
        """ Instantiate this class optionally with a JSON string serialized from this class
        (what is sent by Scipion to this web service)."""

        self._prots = dict()
        if jsonStr is not None:
            self.deserialize(jsonStr)

    def getProtStats(self):
        return self._prots

    def deserialize(self, jsonStr):
        """ Deserialize a JSONString serialized by this class with the toJSON method"""
        jsonObj = json.loads(jsonStr)

        if isinstance(jsonObj, dict):
            self.deserializeV2(jsonObj)
        else:
            self.deserializeList(jsonObj)

    def deserializeV2(self, jsonObj):
        """ Deserializes v2 usage stats: something like {"ProtA": [2,{..}],...} """
        for key, value in jsonObj.items():
            # Value should be something like [2,{..}]
            count = value[0]
            nextProtDict = value[1]
            nextProt = ProtStat(count, nextProtDict)
            self._prots[key] = nextProt

    def deserializeList(self, jsonObj):
        """ Deserializes old data: a list of protocol names repeated: ["ProtA","ProtA", "ProtB", ...] """

        for protName in jsonObj:
            self.addCount(protName)

    def addCount(self, protName):
        """ Adds one to the count of a protocol"""

        protStat = self._prots.get(protName, ProtStat())
        if protName not in self._prots:
            self._prots[protName] = protStat

        protStat.addUsage()

    def addCountToNextProtocol(self, protName, nextProtName):
        protStat = self._prots.get(protName)
        protStat.addCountToNextProtocol(nextProtName)

    def getCount(self):
        """ Returns the number of protocols in the workflow"""
        count = 0
        for ps in self._prots.values():
            count += ps._count
        return count

    def toJSON(self):
        """ Returns a valid JSON string"""
        if len(self._prots) == 0:
            return "{}"
        else:
            jsonStr="{"
            for protName, protStat in self._prots.items():

                jsonStr += '"%s":%s,' % (protName, protStat.toJSON())

            jsonStr = jsonStr[:-1] + "}"

            return jsonStr

    def __repr__(self):
        return self.toJSON()
