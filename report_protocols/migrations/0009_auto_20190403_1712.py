# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-03 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_protocols', '0008_auto_20190329_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protocol',
            name='description',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]