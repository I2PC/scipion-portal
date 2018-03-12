from django.contrib import admin
from forms import PluginForm
from models import Download, Acknowledgement, Plugin

class DownloadAdmin(admin.ModelAdmin):
    list_display = ("fullName", "organization", "country", "subscription", "version", "platform", "creation")
    search_fields = ("fullName", "organization", "country", "email", "platform")
    ordering = ("-creation",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return (False if obj else True)

    def has_delete_permission(self, request, obj=None):
        return True


class AcknowledgementAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'url', 'image')


class PluginAdmin(admin.ModelAdmin):
    form = PluginForm
    list_display = ('name', 'dirName', 'pipName',
                    'pluginSourceUrl', 'binaryVersions', 'pluginVersions')


admin.site.register(Download, DownloadAdmin)
admin.site.register(Acknowledgement, AcknowledgementAdmin)
admin.site.register(Plugin, PluginAdmin)
