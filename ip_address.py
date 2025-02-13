import logging
import time

logger = logging.getLogger(__name__)

import requests
import json

NULL_COUNTRY = "VA"

def get_geographical_information_ip_api(ip):
    """ Returns geographical information using ip_api.com api.
    https://ip-api.com/docs/api:json

    See this for reference: https://ip-api.com/docs/api:json#test

    RESPONSE is like this:

    {
      "status": "success",
      "country": "Canada",
      "city": "Montreal",
      "message": "included only when status is fail Can be one of the following: private range, reserved range, invalid query"
    }

    """

    location_country = NULL_COUNTRY
    location_city = "N/A"

    # Automatically geolocate the connecting IP
    url = 'http://ip-api.com/json/%s?fields=status,country,city' % ip

    # Token is sent as Bearer token
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
    }

    # There is a 45 request limit per minute... let's wait 2 secs to avoid saturating the service
    time.sleep(2)
    response = requests.request("GET", url, headers=headers)

    try:
        location = json.loads(response.text)
        status = location["status"]
        if status=="success":
            location_city = location['city']
            location_country = location['country']
        else:
            logger.warning("ip-api responded with a failed status. %s" % location["message"])
    except Exception as e:
        logger.error("Location for %s could not be determined using ip-api.com.", exc_info=e)

    return (location_country, location_city)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


get_geographical_information=get_geographical_information_ip_api