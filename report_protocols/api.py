from django.core import serializers
from django.db.models import Count
from django.http import HttpResponse
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from django.conf.urls import url
from tastypie.utils import trailing_slash
import json
from collections import Counter
import datetime
import socket
from urllib2 import urlopen
from contextlib import closing


from models import Workflow, Protocol, IpAddressBlackList

class ProtocolResource(ModelResource):
    """allow search in protocol table"""
    class Meta:
        queryset = Protocol.objects.all()
        resource_name = 'protocol'
        filtering = {'name': ALL}
        #allowed_methods = ('get', 'put', 'post', 'delete', 'patch')

class WorkflowResource(ModelResource):
    """allow search in workflow table"""
    class Meta:
        queryset = Workflow.objects.all()
        resource_name = 'workflow'
        filtering = {'project_uuid': ALL}
        #allowed_methods = ('get', 'put', 'post', 'delete', 'patch')

    #agnade al mapeo de urls los webservices que desarrolleis
    def prepend_urls(self):
        return [
            url(r"^(%s)/addOrUpdateWorkflow%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('addOrUpdateWorkflow'), name="api_add_useraddOrUpdateWorkflow"),
            url(r"^(%s)/reportProtocolUsage%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reportProtocolUsage'), name="reportProtocolUsage"),
            url(r"^(%s)/scipionByCountry%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('scipionByCountry'), name="scipionByCountry"),
        ]

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def isInBlackList(self,ip):
        """ check if ip address is in blackList and then return False. 
            Otherwise return True"""
        try:
            IpAddressBlackList.objects.get(client_ip=ip)
        except IpAddressBlackList.DoesNotExist:
            return True
        return False
        
    def get_geographical_information(self, ip):
        location_country = "N/A"
        location_city = "N/A"
        # Automatically geolocate the connecting IP
        url = 'http://freegeoip.net/json/%s'%ip
        print "url", url
        try:
            with closing(urlopen(url)) as response:
                location = json.loads(response.read())
                location_city = location['city']
                location_country = location['country_name']
        except:
            print("Location could not be determined automatically")
        return (location_country, location_city)

    def scipionByCountry(self, request, *args, **kwargs):
        # curl -i  http://localhost:8000/report_protocols/api/workflow/workflow/scipionByCountry/
        # curl -i  http://calm-shelf-73264.herokuapp.com/report_protocols/api/workflow/workflow/scipionByCountry/
        scipion_by_country = Workflow.objects.all().values('client_country').annotate(total=Count('client_country'))

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
        client_ip = self.get_client_ip(request)
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
            self.get_geographical_information(workflow.client_ip)
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
