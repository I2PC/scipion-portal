import boto3

# Create an SNS client
client = boto3.client(
    "sns",
    aws_access_key_id="AKIAIGXWMESOWUVPSKVA",
    aws_secret_access_key="znrE8qhLJLw8wUfqeuY7o7dUWjS+eCqmm4w21lX/",
    region_name="us-east-1"
)

# Send your sms message.
response = client.publish(
    PhoneNumber="+34600055805",
    Message="Hello World!"
)
print("Response: {}".format(response))

