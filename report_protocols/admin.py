from django.contrib import admin
from report_protocols.models import Protocol, Workflow, IpAddressBlackList, Package, ProtocolType, Installation
from web.models import Contribution


class InstallationAdmin(admin.ModelAdmin):
    list_display = ('creation_date', 'lastSeen', 'client_address', 'client_country','scipion_version')
    search_fields = list_display


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('project_uuid',
                    'date',
                    'lastModificationDate',
                    'get_country',
                    'get_address',
                    'timesModified',
                    'prot_count',
                    'scipion_version')
    search_fields = ('project_workflow', 'date', 'installation__client_country', 'installation__client_address', 'timesModified', 'prot_count', 'scipion_version')
    ordering = ("-lastModificationDate",)

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
