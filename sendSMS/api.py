# sendSMS/api.py
from tastypie.resources import ModelResource
from sendSMS.models import SMS
from tastypie.utils import trailing_slash
from django.conf.urls import url
import boto3
from keys import   aws_access_key_id, aws_secret_access_key

class sendMsgResource(ModelResource):
    class Meta:
        resource_name = 'sendmsg'

    #agnade al mapeo de urls los webservices que desarrolleis
    def prepend_urls(self):
        return [
            url(r"^(%s)/sendMsg%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('sendMsg'), name="api_sendMsg"),
        ]

    # curl -i  http://localhost:8000/sendSMS/api/sendSMS/sendmsg/sendMsg/
    # curl -i  http://calm-shelf-73264.herokuapp.com/report_protocols/api/sendSMS/api/sendSMS/sendmsg/sendMsg/
    # curl -i -d "phoneNumber=600055800&message=I love you" http://localhost:8000/sendSMS/api/sendSMS/sendmsg/sendMsg/

    #TODO: check in address
    def sendMsg(self, request, *args, **kwargs):
        #get posted data
        phoneNumber = request.POST['phoneNumber']
        message = request.POST['message']
        ###print "phoneNumber", phoneNumber, "message", message
        # Create an SNS client
        client = boto3.client(
            "sns",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="us-east-1"
        )

        # Send your sms message.
        client.publish(
            PhoneNumber="+34600055805",
            Message="I love you"
        )

        statsDict = {}
        statsDict['error'] = False
        return self.create_response(request, statsDict)


