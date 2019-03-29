from django.contrib import admin
from models import Protocol, Workflow, IpAddressBlackList, Package, ProtocolType

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('project_uuid',
                    'date',
                    'lastModificationDate',
                    'client_address',
                    'client_country',
                    'client_city',
                    'timesModified')
    search_fields = ('project_workflow', 'date', 'client_country', 'client_city', 'timesModified')
    ordering = ("-lastModificationDate",)


class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'pipName', 'description', 'url')
    ordering = ("name", 'pipName')


class ProtocolTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ("name",)


class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name', 'timesUsed', 'package', 'protocolType')
    ordering = ('-timesUsed', "name")


class IpAddressBlackListAdmin(admin.ModelAdmin):
    list_display = ('client_ip', 'note')
    ordering = ('client_ip', 'note')


# Register your models here.
admin.site.register(Protocol, ProtocolAdmin)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(IpAddressBlackList, IpAddressBlackListAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(ProtocolType, ProtocolTypeAdmin)


