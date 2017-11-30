from django.contrib import admin
from models import Download

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

admin.site.register(Download, DownloadAdmin)
