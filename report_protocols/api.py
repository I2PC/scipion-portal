import logging
logger = logging.getLogger(__name__)
from django import utils
from django.http import HttpResponse, HttpResponseBadRequest
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from django.conf.urls import url
from tastypie.utils import trailing_slash
import json
from collections import Counter
import socket

from ip_address import get_client_ip, get_geographical_information
from report_protocols.models import Workflow, Protocol, IpAddressBlackList, Package, Installation
from web.models import Acknowledgement, Contribution


class ProtocolResource(ModelResource):
    """allow search in protocol table"""
    class Meta:
        queryset = Protocol.objects.all()
        resource_name = 'protocol'
        filtering = {'name': ALL}
        allowed_methods = ('get', 'post')
        # Add resource urls

    def prepend_urls(self):
        return [
            url(r"^(%s)/batchupdate%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('batchupdate'), name="protocol_batch_update")
            ]

    def batchupdate(self, request, * args, **kwargs):
        """receive a json dictionary with protocols info
           store the dictionary in protocols table
           Expected json format should be like:
           [
              {"name": "prot1", "description": "this protocol ....", "friendlyName": "nice name"},
              {"name": "prot2", "description": "this protocol2 ....", "friendlyName": "nice name2"}
              ...
           ]
        """
        # Since prepended url do not handle authorization we need to do it here
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Verify user
        protocolsJson = request.body
        protocolsList = json.loads(protocolsJson)


        def chooseValue(new, old):

            return old if new == "" else new

        # For each package
        for protocol in protocolsList:

            protName = protocol["name"]
            packageName = protocol["package"]

            # If it exists
            dbProtocol = Protocol.objects.filter(name__iexact=protName).first()

            if not dbProtocol:
                dbProtocol = Protocol.objects.create(name=protName)
            dbProtocol.description = chooseValue(protocol["description"], dbProtocol.description)
            dbProtocol.friendlyName = chooseValue(protocol["friendlyName"], dbProtocol.friendlyName)

            # Try to get the package
            dbPackage = Package.objects.filter(name__iexact=packageName).first()
            if not dbPackage:
                dbPackage = Package.objects.create(name=packageName)
            dbProtocol.package = dbPackage

            dbProtocol.save()

        return self.create_response(request, protocolsList)


class WorkflowResource(ModelResource):
    """allow search in workflow table"""
    class Meta:
        queryset = Workflow.objects.all()
        resource_name = 'workflow'
        filtering = {
            'project_uuid': ALL,
            'timesModified': ['gte', 'gt', 'lte', 'lt']
        }
        #allowed_methods = ('get', 'put', 'post', 'delete', 'patch')

    # Add resource urls
    def prepend_urls(self):
        return [
            url(r"^(%s)/addOrUpdateWorkflow%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('addOrUpdateWorkflow'), name="api_add_useraddOrUpdateWorkflow"),
            url(r"^(%s)/reportProtocolUsage%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reportProtocolUsage'), name="reportProtocolUsage"),
            url(r"^(%s)/updateWorkflowsGeoInfo%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('updateWorkflowsGeoInfo'), name="updateWorkflowsGeoInfo"),
            url(r"^(%s)/full%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('full'), name="full"),
            url(r"^(%s)/refreshWorkflows%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('refreshWorkflows'), name="refreshWorkflows"),
            url(r"^(%s)/testIpAPI%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('testIpAPI'), name="testIpAPI"),

        ]

    def isInBlackList(self,ip):
        """ check if ip address is in blackList and then return False. 
            Otherwise return True"""
        try:
            IpAddressBlackList.objects.get(client_ip=ip)
        except IpAddressBlackList.DoesNotExist:
            return True
        return False

    def full(self, request, *args, **kwargs):
        # curl -i  http://localhost:8000/report_protocols/api/workflow/workflow/full/
        filterDict = dict(request.GET.iterlists())

        filter = dict()
        for key, value in filterDict.iteritems():
            filter[key] = value[0]
        print filter

        scipion_by_country = Workflow.objects.filter(**filter).values(
            "installation__client_country", "timesModified", "date", "lastModificationDate", "prot_count"
        )

        from django.core.serializers.json import DjangoJSONEncoder
        json_data = json.dumps(list(scipion_by_country), cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type='application/json')


    def addOrUpdateWorkflow(self, request, * args, **kwargs):
        """receive a json dictionary with protocols
           store the dictionary in workflow table
           increase the number of times attribute
           parse dictionary and updates protocol usage in protocol table
           #should you need to debug the following commands may come handy
           curl -i -d "project_uuid=hh&project_workflow=kk" http://localhost:8000/report_protocols/api/workflow/workflow/addOrUpdateWorkflow/
           #curl -i  http://secret-reaches-65198.herokuapp.com/report_protocols/api/workflow/workflow/?project_uuid=ed566c70-3118-4722-86ad-06f1f6e77e74
           curl -i  http://calm-shelf-73264.herokuapp.com/report_protocols/api/workflow/workflow/?project_uuid=ed566c70-3118-4722-86ad-06f1f6e77e74
           curl -i -d "project_uuid=hh&project_workflow=kk" http://calm-shelf-73264.herokuapp.com/report_protocols/api/workflow/workflow/addOrUpdateWorkflow/
                   """
        client_ip = get_client_ip(request)
        logger.info("Workflow received from %s" % client_ip)

        if self.isInBlackList(client_ip):
            project_uuid = request.POST['project_uuid']
            reported_workflow = request.POST['project_workflow']

            # Guess the version
            version = "3.0" if "/3." in request.META.get('HTTP_USER_AGENT', "") else "2.0"

            # Get the installation or create it
            installation, created = Installation.objects.get_or_create(client_ip=client_ip)

            if created:
                installation.client_address = socket.getfqdn(client_ip)
                installation.client_country, installation.client_city = get_geographical_information(client_ip)
                logger.info("New installation created from %s" % client_ip)

            installation.lastSeen = utils.timezone.now()
            installation.scipion_version = version
            installation.save()

            # Get the workflow or create if
            workflow, wcreated = Workflow.objects.get_or_create(project_uuid=project_uuid)

            # If existed, we need to get the counter before loosing it
            if not wcreated:
                db_workflowCounter = Counter([x.encode('latin-1') for x in json.loads(workflow.project_workflow)])

            workflow.project_workflow = reported_workflow
            workflow.timesModified += 1
            workflow.lastModificationDate = utils.timezone.now()
            workflow.scipion_version = version
            workflow.installation = installation

            workflow.save()

            # Deal with the counter.
            reported_workflowCounter = Counter([x.encode('latin-1') for x in json.loads(reported_workflow)])
            # If workflow already exists substract before adding
            if not wcreated:
                project_workflowDict = reported_workflowCounter - db_workflowCounter
            else:
                project_workflowDict = reported_workflowCounter

            for protocolName, numberTimes in project_workflowDict.iteritems():
                if Protocol.objects.filter(name=protocolName).exists():
                    protocolObj = Protocol.objects.get(name=protocolName)
                else:
                    protocolObj = Protocol(name=protocolName)
                protocolObj.timesUsed += numberTimes
                protocolObj.save()

        statsDict = {}
        statsDict['msg'] = "Installation %s, Workflow %s for ip %s." % ("created" if created else "updated",
                                                                        "created" if wcreated else "updated",
                                                                        client_ip)
        statsDict['error'] = False
        return self.create_response(request, statsDict)

    def refreshWorkflows(self, request, *args, **kwargs):
        """ Load and save all protocols to calculate prot_count and maybe future calculated values.
        URL: report_protocols/api/workflow/workflow/refreshWorkflows/
          """
        statsDict = {}

        # Get the workflows with missing geo info
        for workflow in Workflow.objects.all():

            # Save it
            workflow.save()

        statsDict['error'] = False

        return self.create_response(request, statsDict)


    def testIpAPI(self, request, *args, **kwargs):
        """ test if ip to location service is working
        URL: report_protocols/api/v2/workflow/testIpAPI/?ip=1.2.3.42.155.212.55
        """

        ip = request.GET.get("ip", None)

        country, city = get_geographical_information(ip)

        return self.create_response(request, {"msg": "ip: %s, country: %s, city: %s" % ( ip, country, city),
                                       "error": "None"})

    def updateWorkflowsGeoInfo(self, request, *args, **kwargs):
        """ Query all workflows that do not have GEO info and tries to get it
          """
        statsDict = {}

        limit = request.POST.get("limit", 100)
        count = 0
        # Get the workflows with missing geo info
        for installation in Installation.objects.filter(client_country="VA"):

            # Request GeoInfo
            installation.client_country, installation.client_city = \
                get_geographical_information(installation.client_ip)

            # Save it
            installation.save()

            count += 1

            if count >=limit:
                break

            # Annotate stats

        statsDict["msg"] = "%s workflows scanned." % count
        statsDict['error'] = False

        return self.create_response(request, statsDict)


    def reportProtocolUsage(self, request, * args, **kwargs):
        """ask for a protocol histogram"""
        pass

class PackageResource(ModelResource):
    """allow search in workflow table"""
    class Meta:
        queryset = Package.objects.all()
        resource_name = 'package'
        #allowed_methods = ('get', 'put', 'post', 'delete', 'patch')
        authentication = BasicAuthentication()
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(%s)/batchupdate%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('batchupdate'), name="package_batch_update"),
            url(r"^(%s)/updatecollaborators%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('updatecollaborators'), name="package_collaborators")
            ]

    def batchupdate(self, request, * args, **kwargs):
        """receive a json dictionary with packages info
           store the dictionary in packages table
           Expected json format should be like:
           [
              {"name": "package1", "url": "http:sdsdds", "description": "blah blah blah"},
              ...
           ]
        """
        # Since prepended url do not handle authorization we need to do it here
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        packagesJson = request.body
        packagesList = json.loads(packagesJson)

        # For each package
        for package in packagesList:

            # If it exists
            dbPackage = Package.objects.filter(name__iexact=package["name"]).first()

            if not dbPackage:
                dbPackage = Package.objects.create(name=package["name"])
                
            dbPackage.url = package["url"]
            dbPackage.description = package["description"]
            dbPackage.save()

        return self.create_response(request, packagesList)

    def updatecollaborators(self, request, *args, **kwargs):
        """receive a json dictionary with packages info
           store the dictionary in packages table
           Expected json format should be like:
           [
              {"package": "package1",
               "packageurl": "http://sds"
               "githubName": "octouser1",
               "name": "John Smith",
               "url": "-->github user url"
               "image": "avatar url"},
              ...
           ]
        """
        # Since prepended url do not handle authorization we need to do it here
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        collaboratorsJson = request.body
        collaborators = json.loads(collaboratorsJson)

        # For each package
        for collaborator in collaborators:

            packageName = collaborator["package"]

            # Get the package by name
            package = Package.objects.filter(name__iexact=packageName).first()

            if not package:
                return HttpResponseBadRequest("Package %s not found." % packageName)

            # If it exists by githubName
            collab = Acknowledgement.objects.filter(githubName=collaborator["githubName"]).first()

            # try name
            if not collab:
                collab = Acknowledgement.objects.filter(githubName=collaborator["name"]).first()

                # Otherwise is a new one
                if not collab:
                    collab = Acknowledgement.objects.create()
                    collab.description = "Contributed to Scipion framework."
                    collab.title = collaborator["name"]


            collab.githubName = collaborator["githubName"]
            collab.url = collaborator["url"]
            collab.image = collaborator["image"]

            # Save the collaborator
            collab.save()

            # Save the collaboration
            contribution, created = Contribution.objects.get_or_create(package=package,
                                                              contributor=collab)
            contribution.save()

        return self.create_response(request, collaborators)


class InstallationResource(ModelResource):
    """allow search in installation table"""
    class Meta:
        max_limit = 0
        queryset = Installation.objects.all()
        resource_name = 'installations'
        filtering = {
            'creation_date': ALL,
            'lastSeen': ALL,
            'client_ip': ALL,
            'client_address': ALL,
            'client_country': ALL,
            'client_city': ALL,
            'scipion_version':ALL
        }
        #allowed_methods = ('get', 'put', 'post', 'delete', 'patch')

    # Add resource urls
    def prepend_urls(self):
        return [
            url(r"^(%s)/full%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('full'), name="full"),
        ]


    def full(self, request, *args, **kwargs):
        # curl -i  http://localhost:8000/report_protocols/api/v2/installations/full/
        filterDict = dict(request.GET.iterLists())

        filter = dict()
        for key, value in filterDict.iterItems():
            filter[key] = value[0]
        print(filter)

        installations = Installation.objects.filter(**filter).values(
                        'creation_date', 'lastSeen', 'client_country', 'client_city', 'scipion_version'
        )

        from django.core.serializers.json import DjangoJSONEncoder
        json_data = json.dumps(list(installations), cls=DjangoJSONEncoder)
        return HttpResponse(json_data, content_type='application/json')



