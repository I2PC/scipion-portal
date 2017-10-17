# -*- coding: utf-8 -*-
from __future__ import unicode_literals


# Register your models here.
from django.contrib import admin
from create_proj.models import Microscope, Acquisition, Workflow, ScipionBox, Acquisition2

admin.site.register(Microscope)
admin.site.register(Acquisition)
admin.site.register(Acquisition2)
admin.site.register(Workflow)
admin.site.register(ScipionBox)