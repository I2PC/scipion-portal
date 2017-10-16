# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from django.conf import settings

# workflow
class Workflow(models.Model):
    name = models.CharField(max_length=128, blank=False)
    workflow = models.TextField(unique=True, blank=False)
    date = models.DateTimeField(default=datetime.now, blank=True)

    def __unicode__(self):  #For Python 2, use __str__ on Python 3
        return self.name

# Create your models here.
class Microscope(models.Model):
    name     = models.CharField(max_length=64, unique=True, blank=False)
    detector = models.CharField(max_length=64, unique=True, default='FalconIII')
    detectorPixelSize = models.FloatField(default=14)  # microns
    cs = models.FloatField(default=2.7)  # mm
    # microscope data is in this folder
    dataFolder = models.CharField(max_length=256,
                                  default='/home/scipionuser/OffloadData')

    def __unicode__(self):  #For Python 2, use __str__ on Python 3
        return self.name

PIXELSIZE_CHOICES = [(1., '1'), (3., '3')]
class Acquisition(models.Model):
    microscope = models.ForeignKey(Microscope, default=1)
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False)
    workflow   = models.ForeignKey(Workflow, default=1)
    sample     = models.CharField(max_length=128)
    voltage    = models.IntegerField(default=200)
    date       = models.DateTimeField(default=datetime.now, blank=True)
    projname   = models.CharField(max_length=128)
    #backupPath = models.FilePathField(blank=True)
    backupPath = models.FilePathField(path='/', allow_folders=True,
                                       allow_files=False)

    def save(self, *args, **kwargs):
        self.projname = "%s_%s_%s"%(self.date.strftime('%Y_%m_%d'),
                                    self.user.name, self.sample)

    def __unicode__(self):  #For Python 2, use __str__ on Python 3
        return "user=%s, sample=%s, date=%s"%(self.user,
                                            self.sample,
                                            self.date.strftime('%Y-%m-%d '
                                                               '%H:%M'))



#class Acquisition2(models.Model):
#    dose       = models.FloatField(blank=False)
#    pixelsize  = models.FloatField(choices=PIXELSIZE_CHOICES,
#                            default=3.)


#not sure about this clase may be we can rely on workflow
class ScipionBox(models.Model):
    #project Name
    name = models.CharField(max_length=128, blank=False)
    # Default backup directory (usually usb mount point
    data_backup = models.CharField(max_length=256, default='/media/scipionuser')
    # Name for the Scipion project inside the session folder
    #scipion_project = models.FilePathField(
    #        default='/home/scipionuser/ScipionUserData/projects')
    # Pattern to be used when importing movies
    pattern = models.CharField(max_length=256,
                               default = 'GRID_??/DATA/Images-Disc?/'
                                         'GridSquare_*/Data/FoilHole_\
                                         *frames.mrc')
    # HTML report settings <- rely on workflow?
    html_publish = \
        models.CharField(max_length=256, default='rsync -av %(REPORT_FOLDER)s '
                         'scipionbox@nolan:/home/scipionbox/public_html/')

    # Email notification settings <- rely on workflow
    email_notification = models.BooleanField(default=False)
    smtp_server = models.CharField(max_length=256, default='localhost')
    smtp_from = models.CharField(max_length=256,
                                 default='noreply-biocomp@cnb.csic.es')
    smtp_to = models.CharField(max_length=256, default='user@domain')

