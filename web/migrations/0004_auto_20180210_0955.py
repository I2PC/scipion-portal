# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-10 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20180206_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acknowledgement',
            name='image',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='acknowledgement',
            name='url',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
