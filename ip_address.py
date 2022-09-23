
import os

from webservices.local_settings import IPXAPI_TOKEN

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webservices.settings')
import django
django.setup()
from urllib.request import urlopen
from contextlib import closing
import json

def get_geographical_information_ipXapi(ip):
    """ Returns geographical information using ipXapi api.

    RESPONSE is like this:

    {
          "status": "success",
          "country": "Spain",
          "countryCode": "ES",
          "region": "MD",
          "regionName": "Madrid",
          "city": "Madrid",
          ...
    }

    """

    location_country = "VA"
    location_city = "N/A"

    # Automatically geolocate the connecting IP
    url = 'https://ipxapi.com/api/ip?ip=%s' % ip

    import requests

    # Token is sent as Bearer token
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "Bearer %s" % IPXAPI_TOKEN,
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers)

    try:
        location = json.loads(response.text)
        location_city = location['city']
        location_country = location['country']
    except Exception as e:
        print("Location could not be determined automatically: %s" % e)


    #request = Request(url, headers=headers, method="GET")
    # try:
    #     with closing(urlopen(request)) as response:
    #         location = json.loads(response.read())
    #         location_city = location['city']
    #         location_country = location['country']
    # except Exception as e:
    #     print("Location could not be determined automatically: %s" % e)

    return (location_country, location_city)

def get_geographical_information_ipstack(ip):

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


get_geographical_information=get_geographical_information_ipXapi