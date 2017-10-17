# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils.text import slugify
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

class Acquisition(models.Model):
    microscope = models.ForeignKey(Microscope, default=settings.DEFAULTMIC)
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False)
    workflow   = models.ForeignKey(Workflow, default=settings.DEFAULTWORKFLOW)
    sample     = models.CharField(max_length=128)
    voltage    = models.IntegerField(default=200)
    date       = models.DateTimeField(default=datetime.now, blank=True)
    projname   = models.CharField(max_length=128, blank=True, unique=True)
    backupPath = models.FilePathField(path=settings.BACKUPPATH, allow_folders=True,
                                       allow_files=False)

    def save(self, *args, **kwargs):
        #create project name
        user_name = slugify(self.user.name)
        self.projname = "%s_%s_%s"%(self.date.strftime('%Y_%m_%d'),
                                    user_name, self.sample)
        super(Acquisition, self).save(*args, **kwargs)

    def __unicode__(self):  #For Python 2, use __str__ on Python 3
        try:
            return "user=%s, sample=%s, date=%s"%(self.user,
                                                  self.sample,
                                                  self.date.strftime('%Y-%m-%d '
                                                                   '%H:%M'))
        except:
            return "sample=%s, date=%s"%(self.sample,
                                         self.date.strftime('%Y-%m-%d '
                                                                   '%H:%M'))


DRIFT_MEASU_CHOICES = [('never', 'never'), ('always', 'always'),('gridsquare','gridsquare')]
EXPOSURE_HOLE_CHOICES = [(1, '1'), (2, '2'),(3, '3')]
C2_CHOICES = [(30, '30'), (50, '50'),(70, '70'),(150, '150')]
O1_HOLE_CHOICES = [(30, '30'), (70, '70')]
PHP_CHOICES = [(1, '1'), (2, '2'),(3, '3'), (4, '4'), (5, '5'), (6, '6')]

class Acquisition2(models.Model):
    acquisition = models.ForeignKey(Acquisition)
    nominal_magnification = models.FloatField(blank=True)
    pixelsize = models.FloatField(blank=False)  # A/px
    spotsize = models.FloatField(blank=True)
    illuminated_area = models.FloatField(blank=True)
    dose_per_pixel = models.FloatField(blank=False)  # e/px
    total_exposure_time = models.FloatField(blank=False)
    number_of_fractions = models.PositiveIntegerField(blank=False)
    frames_in_fraction = models.PositiveIntegerField(blank=False)
    nominal_defocus_min = models.IntegerField(blank=True)
    nominal_defocus_max = models.IntegerField(blank=True)
    autofocus = models.FloatField(blank=True)
    drift_meassurement = models.CharField(max_length=16, choices=DRIFT_MEASU_CHOICES,
                                          default='never')
    delay_after_stage_shift = models.IntegerField(default=10)
    delay_after_image_shift = models.IntegerField(default=5)
    max_image_shift = models.IntegerField(default=3)
    exposure_hole = models.IntegerField(choices=EXPOSURE_HOLE_CHOICES,
                                      default=1)
    c2 = models.IntegerField(choices=C2_CHOICES,
                                      default=50)
    o1 = models.IntegerField(choices=O1_HOLE_CHOICES,
                                      default=70)
    php = models.IntegerField(choices=PHP_CHOICES,
                                      default=3)

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

