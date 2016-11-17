from tastypie.resources import ModelResource
from tastypie.constants import ALL
from django.conf.urls import url
from tastypie.utils import trailing_slash

from report_protocols.models import Workflow

class WorkflowResource(ModelResource):
    class Meta:
        queryset = Workflow.objects.all()
        resource_name = 'workflow'
        filtering = {'hash': ALL}

    #agnade al mapeo de urls los webservices que desarrolleis
    def prepend_urls(self):
        return [
            url(r"^(%s)/addOrUpdateWorkflow%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('addOrUpdateWorkflow'), name="api_add_useraddOrUpdateWorkflow"),
            url(r"^(%s)/reportProtocolUsage%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reportProtocolUsage'), name="reportProtocolUsage"),
        ]

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def addOrUpdateWorkflow(self, request, * args, **kwargs):
        """curl -i -d "hash=hh&json=kk" http://localhost:8000/report_protocols/api/workflow/workflow/addOrUpdateWorkflow/
        """
        project_uuid = request.POST['project_uuid']
        project_workflow = request.POST['project_workflow']
        #print "project_uuid",project_uuid
        #print "project_workflow",project_workflow
        workflow, error = Workflow.objects.get_or_create(project_uuid=project_uuid)
        workflow.project_workflow = project_workflow
        workflow.client_ip = self.get_client_ip(request)
        workflow.save()
        statsDict = {}
        statsDict['error'] = False
        return self.create_response(request, statsDict)

    def reportProtocolUsage(self, request, * args, **kwargs):
        """ask for a protocol histogram"""
        pass