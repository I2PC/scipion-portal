"""
WSGI config for webservices project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import django

from django.core.wsgi import get_wsgi_application
from django.core.handlers.wsgi import WSGIHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webservices.settings")

class WSGIEnvironment(WSGIHandler):
    def __call__(self, environ, start_response):
        os.environ['SCIPION_CONFIG'] = environ.get('SCIPION_CONFIG', os.environ.get('SCIPION_CONFIG'))
        os.environ['DATABASE_URL'] = environ.get('DATABASE_URL', os.environ.get('DATABASE_URL'))
        django.setup()
        return super(WSGIEnvironment, self).__call__(environ, start_response)

application = WSGIEnvironment()


