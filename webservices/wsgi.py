"""
WSGI config for webservices project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

import django
from django.core.handlers.wsgi import WSGIHandler

os.environ["DJANGO_SETTINGS_MODULE"] = "webservices.settings"

django.setup()

application = WSGIHandler()

