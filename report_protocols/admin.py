from django.contrib import admin
from report_protocols.models import Protocol, Workflow

#class ProtocolAdmin(admin.ModelAdmin):
#    list_display = ('name', 'timesUsed')
#    ordering = ("-timesUsed")

# Register your models here.
admin.site.register(Protocol)
admin.site.register(Workflow)
