from django.contrib import admin
from report_protocols.models import Protocol, Workflow

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('project_uuid', 'date','client_ip','timesModified')
    ordering = ("date",)

# Register your models here.
admin.site.register(Protocol)
admin.site.register(Workflow, WorkflowAdmin)


