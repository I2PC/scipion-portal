# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-20 11:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_protocols', '0005_auto_20161120_1000'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='protocol',
            options={'ordering': ('-timesUsed', 'name')},
        ),
        migrations.AlterField(
            model_name='protocol',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
