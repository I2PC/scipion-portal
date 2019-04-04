from django.db.models import Count
from django.http import HttpResponse
from tastypie.authentication import BasicAuthentication, Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from django.conf.urls import url
from tastypie.utils import trailing_slash
import json
from collections import Counter
import datetime
import socket

from ip_address import get_client_ip, get_geographical_information
from models import Workflow, Protocol, IpAddressBlackList, Package


class ProtocolResource(ModelResource):
    """allow search in protocol table"""
    class Meta:
        queryset = Protocol.objects.all()
        resource_name = 'protocol'
        filtering = {'name': ALL}
        #allowed_methods = ('get', 'put', 'post', 'delete', 'patch')
        authentication = BasicAuthentication()
        authorization = Authorization()
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
        # Since prepended url do not handle auhtorization we need to do it here
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

            # If it exists
            dbProtocol, created = Protocol.objects.get_or_create(name=protocol ["name"])
            dbProtocol.description = chooseValue(protocol["description"], dbProtocol.description)
            dbProtocol.friendlyName = chooseValue(protocol["friendlyName"], dbProtocol.friendlyName)
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
            url(r"^(%s)/scipionByCountry%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('scipionByCountry'), name="scipionByCountry"),
            url(r"^(%s)/updateWorkflowsGeoInfo%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('updateWorkflowsGeoInfo'), name="updateWorkflowsGeoInfo"),
        ]

    def isInBlackList(self,ip):
        """ check if ip address is in blackList and then return False. 
            Otherwise return True"""
        try:
            IpAddressBlackList.objects.get(client_ip=ip)
        except IpAddressBlackList.DoesNotExist:
            return True
        return False

    def scipionByCountry(self, request, *args, **kwargs):
        # curl -i  http://localhost:8000/report_protocols/api/workflow/workflow/scipionByCountry/
        # curl -i  http://calm-shelf-73264.herokuapp.com/report_protocols/api/workflow/workflow/scipionByCountry/
        filterDict = dict(request.GET.iterlists())

        filter = dict()
        for key, value in filterDict.iteritems():
            filter[key] = value[0]
        print filter

        scipion_by_country = Workflow.objects.filter(**filter)\
            .values('client_country')\
            .annotate(total=Count('client_country'))

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
        if self.isInBlackList(client_ip):    
            project_uuid = request.POST['project_uuid']
            project_workflow = request.POST['project_workflow']
            project_workflowCounter = Counter([x.encode('latin-1') for x in json.loads(project_workflow)])

            workflow, created = Workflow.objects.get_or_create(project_uuid=project_uuid)
            if not created:
                dabase_workflowCounter  = Counter([x.encode('latin-1') for x in json.loads(workflow.project_workflow)])
            else:
                dabase_workflowCounter  = Counter([x.encode('latin-1') for x in json.loads(project_workflow)])

            workflow.project_workflow = project_workflow

            workflow.client_ip = client_ip
            workflow.client_address = socket.getfqdn(workflow.client_ip)
            workflow.client_country, workflow.client_city = \
            get_geographical_information(workflow.client_ip)
            workflow.timesModified += 1
            workflow.lastModificationDate = datetime.datetime.now()
            workflow.save()

            #if workflow already exists substract before adding
            if not created:
                project_workflowDict =  project_workflowCounter - dabase_workflowCounter
            else:
                project_workflowDict =project_workflowCounter

            for protocolName, numberTimes in project_workflowDict.iteritems():
                if Protocol.objects.filter(name=protocolName).exists():
                    protocolObj = Protocol.objects.get(name=protocolName)
                else:
                    protocolObj = Protocol(name=protocolName)
                protocolObj.timesUsed += numberTimes
                protocolObj.save()
        statsDict = {}
        statsDict['error'] = False
        return self.create_response(request, statsDict)

    def updateWorkflowsGeoInfo(self, request, *args, **kwargs):
        """ Query all workflows that does not have GEO info and tries to get it
          """
        statsDict = {}

        # Get the workflows with missing geo info
        for workflow in Workflow.objects.filter(client_country="N/A"):

            # Request GeoInfo
            workflow.client_country, workflow.client_city = \
                get_geographical_information(workflow.client_ip)

            # Save it
            workflow.save()

            # Annotate stats


        statsDict['error'] = False

        return self.create_response(request, statsDict)


    def deleteObject(self, request):
        project_uuid = request.POST['project_uuid']
        workflows = Workflow.objects.all()
        if workflows.exists():
            workflows[0].delete()
        statsDict = {}
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
                self.wrap_view('batchupdate'), name="package_batch_update")
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
            dbPackage, created = Package.objects.get_or_create(name=package["name"])
            dbPackage.url = package["url"]
            dbPackage.description = package["description"]
            dbPackage.save()

        return self.create_response(request, packagesList)

