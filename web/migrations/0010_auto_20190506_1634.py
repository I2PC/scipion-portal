# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-06 16:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_auto_20190409_1006'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='acknowledgement',
            options={'verbose_name': 'Contributor', 'verbose_name_plural': 'Contributors'},
        ),
    ]
