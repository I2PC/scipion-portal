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
        ]

    def addOrUpdateWorkflow(self, request, * args, **kwargs):
        """curl -i -d "hash=hh&json=kk" http://localhost:8000/report_protocols/api/workflow/workflow/addOrUpdateWorkflow/
        """
        hash = request.POST['hash']
        json = request.POST['json']
        print "hash,json", hash, json
        workflow, error = Workflow.objects.get_or_create(hash=hash)
        print "workflow, error",workflow, error
        workflow.json = json
        workflow.save()
        statsDict = {}
        statsDict['error'] = False
        return self.create_response(request, statsDict)
