from django.contrib import admin
from models import Download, Acknowledgement, Bundle


class DownloadAdmin(admin.ModelAdmin):
    list_display = ('country', 'version', 'platform', 'creation')
    search_fields = ('country', 'platform', 'version', 'size', 'creation')
    ordering = ("-creation",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return (False if obj else True)

    def has_delete_permission(self, request, obj=None):
        return True


class BundleAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('id', 'version', 'platform', 'size', 'date', 'deprecated')

class AcknowledgementAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'url', 'image')


admin.site.register(Download, DownloadAdmin)
admin.site.register(Acknowledgement, AcknowledgementAdmin)
admin.site.register(Bundle, BundleAdmin)