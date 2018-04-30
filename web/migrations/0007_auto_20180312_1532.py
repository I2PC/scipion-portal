# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-12 15:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_auto_20180312_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plugin',
            name='dirName',
            field=models.CharField(help_text='name of folder in pip package', max_length=256),
        ),
        migrations.AlterField(
            model_name='plugin',
            name='name',
            field=models.CharField(help_text='name used to install', max_length=256),
        ),
    ]