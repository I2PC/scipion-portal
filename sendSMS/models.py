# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
#store sms, just in case
from phonenumber_field.modelfields import PhoneNumberField

class SMS(models.Model):
    msg = models.CharField(max_length=255)
    phone_number = PhoneNumberField()

    def __str__(self):
        return '{phone_number}{msg}'.format(
            phone_number=str(self.phone_number),
            msg=self.msg 
        )
