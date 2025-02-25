import logging
logger = logging.getLogger(__name__)
from django.contrib import admin,messages
from django.db.models import Count
import ip_address
from ip_address import get_geographical_information
from report_protocols.models import Protocol, Workflow, IpAddressBlackList, Package, ProtocolType, Installation, \
    NextProtocol
from web.models import Contribution

class InstallationAdmin(admin.ModelAdmin):
    list_filter = ['creation_date', 'lastSeen', 'scipion_version', 'client_country']
    search_fields = list_filter + ['client_city', 'client_address', 'client_ip']
    list_display = search_fields + ["workflows_count", "months_dead"]
    actions =['update_installations_geo_info', 'prune_installations', 'prune_old_installations']
    @admin.action(description="Update Geographical information: city, country.")
    def update_installations_geo_info(self, request, queryset):
        """ Query all workflows that do not have GEO info and tries to get it """

        attempts = 0
        failed = 0
        # Get the workflows selected
        for installation in queryset:

            attempts += 1
            # Request GeoInfo
            installation.client_country, installation.client_city = \
                get_geographical_information(installation.client_ip)

            # Save it
            if installation.client_country != ip_address.NULL_COUNTRY:
                installation.save()
            else:
                failed += 1

        self.message_user(
            request,
            "%d attempts done. %d failed." % (attempts, failed),
            messages.SUCCESS,
        )

    @admin.action(description="Prune installations without workflows")
    def prune_installations(self, request, queryset):
        """ Prune installations without workflows """

        deleted = 0

        # Get the workflows selected
        for installation in queryset:

            # Get workflows count
            if installation.workflows_count ==0:

                installation.delete()
                deleted +=1

        self.message_user(
            request,
            "%d installations deleted." % deleted,
            messages.SUCCESS,
        )

    @admin.action(description="Prune old installations. Not seen in the last 3 years.")
    def prune_old_installations(self, request, queryset):
        """ Prune installations without workflows """

        deleted = 0

        # Get the workflows selected
        for installation in queryset:

            # Get workflows count
            if installation.months_dead >=36:
                installation.delete()
                deleted += 1

        self.message_user(
            request,
            "%d installations deleted." % deleted,
            messages.SUCCESS,
        )

    def workflows_count(self, obj):
        return obj.workflows_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(workflows_count=Count("workflow"))
        return queryset
class WorkflowAdmin(admin.ModelAdmin):
    common = ['project_uuid',
            'date',
            'lastModificationDate',
            'timesModified',
            'prot_count',
            'scipion_version',
            'project_workflow']
    list_display = common + ['get_country','get_address']
    list_filter = ('date', 'installation__client_country', 'scipion_version')

    search_fields = common +["installation__client_country", "installation__client_city", "installation__client_address"]
    ordering = ("-lastModificationDate",)
    actions = ["updateWorkflows", "recalculateCount" ]

    @admin.action(description="Count protocols and delete empty workflows")
    def updateWorkflows(self, request, queryset):

        updated = 0
        deleted = 0

        for workflow in queryset:
            if workflow.isEmpty():
                workflow.delete()
                deleted += 1
            else:
                workflow.save()
                updated += 1

        self.message_user(
            request,
            "%d workflows deleted. %d updated." % (deleted, updated),
            messages.SUCCESS,
        )

    @admin.action(description="Recalculate the usage of the protocols (selection ignored))")
    def recalculateCount(self, request, queryset):
        """ Recalculates the count of all protocol usage """
        # self.is_authenticated(request)

        # Reset the count
        Protocol.reset_prot_count()

        for workflow in Workflow.objects.all():
            protCount, nextProtCount = workflow.getProtocolsCountDiff()

            workflow.saveProtCount(protCount)
            workflow.saveNextProtCount(nextProtCount)

    def get_country(self, obj):
        if obj.installation is None:
            return "MISSING INSTALLATION"
        else:
            return obj.installation.client_country

    def get_address(self, obj):
        if obj.installation is None:
            return "MISSING INSTALLATION"
        else:
            return obj.installation.client_address

    get_country.short_description = 'Country'
    get_country.admin_order_field = 'client_country'

class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'pipName', 'description', 'package_prot_count', 'url')
    ordering = ("name", 'pipName')

    def package_prot_count(self, obj):
        return obj.protocol_set.count()

    package_prot_count.short_description = "Prot count"


class ProtocolTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ("name",)


class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name', 'timesUsed', 'friendlyName', 'description', 'package', 'protocolType')
    ordering = ('-timesUsed', "name")
    search_fields = ('name', 'timesUsed', 'friendlyName', 'description', 'package__name', 'protocolType__name')
    actions = ["prune_protocols"]

    @admin.action(description="Prune protocols: empty ones(0 usage and no description) and duplicated ones")
    def prune_protocols(self, request, queryset):

        deleted = []
        visited = []
        duplicated = []
        for protocol in queryset:
            name = protocol.name

            if name in visited:
                duplicated.append(name)

            if protocol.timesUsed == 0 and not protocol.friendlyName:
                protocol.delete()
                deleted.append(protocol.name)
            visited.append(protocol.name)
        self.message_user(
            request,
            "%d protocols deleted: %s. Duplicated protocols: %s" % (len(deleted), deleted, duplicated),
            messages.SUCCESS,
        )

class NextProtocolAdmin(admin.ModelAdmin):
    list_display = ('protocol', 'next_protocol', 'count')

class IpAddressBlackListAdmin(admin.ModelAdmin):
    list_display = ('client_ip', 'note')
    ordering = ('client_ip', 'note')

class ContributionAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'package')
    search_fields = ('package__name', 'contributor__title')

# Register your models here.
admin.site.register(Protocol, ProtocolAdmin)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(IpAddressBlackList, IpAddressBlackListAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(ProtocolType, ProtocolTypeAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(Installation, InstallationAdmin)
admin.site.register(NextProtocol, NextProtocolAdmin)

