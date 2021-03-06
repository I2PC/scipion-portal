# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-09 10:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report_protocols', '0011_auto_20190404_1452'),
        ('web', '0008_auto_20190329_1711'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='acknowledgement',
            name='githubName',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='contribution',
            name='contributor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Acknowledgement'),
        ),
        migrations.AddField(
            model_name='contribution',
            name='package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='report_protocols.Package'),
        ),
    ]
