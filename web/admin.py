from django.contrib import admin
from web.models import Acknowledgement

class AcknowledgementAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'url', 'image')


admin.site.register(Acknowledgement, AcknowledgementAdmin)
