from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL
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
