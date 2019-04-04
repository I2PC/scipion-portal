# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-28 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report_protocols', '0005_package_pipname'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='description',
            field=models.CharField(blank=True, default='', max_length=256),
        ),
        migrations.AddField(
            model_name='package',
            name='logo',
            field=models.ImageField(blank=True, upload_to=b'packages'),
        ),
        migrations.AddField(
            model_name='package',
            name='url',
            field=models.CharField(blank=True, default='', help_text='Software site url', max_length=256),
        ),
        migrations.AddField(
            model_name='protocoltype',
            name='icon',
            field=models.ImageField(blank=True, upload_to=b'prot-types'),
        ),
        migrations.AlterField(
            model_name='package',
            name='pipName',
            field=models.CharField(blank=True, default='', help_text='Name of the plugin at pypi.org', max_length=256),
        ),
    ]