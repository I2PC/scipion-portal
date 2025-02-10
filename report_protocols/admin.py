import logging
logger = logging.getLogger(__name__)
from django.contrib import admin,messages

import ip_address
from ip_address import get_geographical_information
from report_protocols.models import Protocol, Workflow, IpAddressBlackList, Package, ProtocolType, Installation
from web.models import Contribution

class InstallationAdmin(admin.ModelAdmin):
    list_display = ('creation_date', 'lastSeen', 'client_address', 'client_country','scipion_version', 'client_ip')
    search_fields = list_display
    list_filter = search_fields
    actions =['updateInstallationGeoInfo']
    @admin.action(description="Update Geographical information: city, country.")
    def updateInstallationGeoInfo(self, request, queryset):
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


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('project_uuid',
                    'date',
                    'lastModificationDate',
                    'get_country',
                    'get_address',
                    'timesModified',
                    'prot_count',
                    'scipion_version',
                    'project_workflow')
    search_fields = ('project_workflow', 'date', 'installation__client_country', 'installation__client_address',
                     'timesModified', 'prot_count', 'scipion_version', 'project_workflow')

    list_filter = search_fields
    ordering = ("-lastModificationDate",)
    actions = ["updateWorkflows"]

    @admin.action(description="Count protocols and set empty workflows to None")
    def updateWorkflows(modeladmin, request, queryset):
        for workflow in queryset:
            workflow.save()

    def get_country(self, obj):
        return obj.installation.client_country

    def get_address(self, obj):
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
