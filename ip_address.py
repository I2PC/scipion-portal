
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webservices.settings')
import django
django.setup()
from report_protocols.models import Workflow
import socket
from urllib2 import urlopen
from contextlib import closing
import json


def get_geographical_information( ip):
    location_country = "N/A"
    location_city = "N/A"
    # Automatically geolocate the connecting IP
    url = 'http://freegeoip.net/json/%s'%ip
    try:
        with closing(urlopen(url)) as response:
            location = json.loads(response.read())
            location_city = location['city']
            location_country = location['country_name']
    except:
        print("Location could not be determined automatically")
    return (location_country, location_city)


workflows = Workflow.objects.all()

for workflow in workflows:
    workflow.client_address = socket.getfqdn(workflow.client_ip)
    workflow.client_country, workflow.client_city = \
        get_geographical_information(workflow.client_ip)
    workflow.save()
