# -*- coding: utf-8 -*-
from __future__ import unicode_literals


# Register your models here.
from django.contrib import admin
from create_proj.models import Microscope, Acquisition, Workflow, ScipionBox

admin.site.register(Microscope)
admin.site.register(Acquisition)
admin.site.register(Workflow)
admin.site.register(ScipionBox)