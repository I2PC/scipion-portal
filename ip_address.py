
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webservices.settings')
import django
django.setup()
from report_protocols.models import Workflow
import socket
from urllib2 import urlopen
from contextlib import closing
import json


def get_geographical_information(ip):

    location_country = "VA"
    location_city = "N/A"
    # Automatically geolocate the connecting IP
    url = 'http://api.ipstack.com/%s?access_key=%s' % (ip,'015c8dc22c593065dd51791ba674205c')
    try:
        with closing(urlopen(url)) as response:
            location = json.loads(response.read())
            location_city = location['city']
            location_country = location['country_name']
    except:
        print("Location could not be determined automatically")
    return (location_country, location_city)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
