from django.contrib import admin
from report_protocols.models import Protocol, Workflow

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('project_uuid', 'date', 'lastModificationDate','client_ip','timesModified')
    ordering = ("-date",)

class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name', 'timesUsed')
    ordering = ('-timesUsed',"name")

# Register your models here.
admin.site.register(Protocol,ProtocolAdmin)
admin.site.register(Workflow, WorkflowAdmin)


