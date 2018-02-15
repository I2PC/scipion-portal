# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-16 09:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_protocols', '0003_auto_20171208_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protocol',
            name='description',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='protocol',
            name='package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='report_protocols.Package'),
        ),
        migrations.AlterField(
            model_name='protocol',
            name='protocolType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='report_protocols.ProtocolType'),
        ),
    ]
