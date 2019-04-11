from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from django.conf.urls import url
from tastypie.utils import trailing_slash
import json
from models import Contribution


class ContributionResource(ModelResource):
    """allow search in protocol table"""
    class Meta:
        queryset = Contribution.objects.all()
        resource_name = 'contribution'
        filtering = {'name': ALL}
        # allowed_methods = ('get', 'put', 'post', 'delete', 'patch')
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

            # If it exists
            dbProtocol, created = Protocol.objects.get_or_create(name=protocol ["name"])
            dbProtocol.description = chooseValue(protocol["description"], dbProtocol.description)
            dbProtocol.friendlyName = chooseValue(protocol["friendlyName"], dbProtocol.friendlyName)
            dbProtocol.save()

        return self.create_response(request, protocolsList)

