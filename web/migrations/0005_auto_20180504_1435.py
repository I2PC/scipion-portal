# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-04 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20180210_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acknowledgement',
            name='image',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='acknowledgement',
            name='url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]