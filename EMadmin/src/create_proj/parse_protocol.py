import os
from django.conf import settings

def parse_ProtImportMovies(protocol, acquisition2):
    acquisition = acquisition2.acquisition
    # get root directory
    dataPath = acquisition.microscope.dataFolder
    projname = acquisition.projname
    projectPath = os.path.join(dataPath, projname)
    protocol['filesPath'] = projectPath + \
                                    '/GRID_??/DATA/Images-Disc1/GridSquare_*/DATA/'
    protocol['voltage'] = acquisition.voltage
    protocol["sphericalAberration"] = acquisition.microscope.cs
    protocol["magnification"] = acquisition2.nominal_magnification
    protocol["samplingRate"] = acquisition2.sampling_rate
    protocol["dosePerFrame"] = acquisition2.dose_per_frame

def parse_ProtMonitorSummary(protocol, acquisition2):
    protocol["emailFrom"] = settings.EMAILFROM
    protocol["emailTo"] = settings.EMAILTO
    protocol["smtp"] = settings.SMTP
    protocol["publishCmd"] = settings.PUBLISHCMD

def parse_protocol(protocol, acquisition2):
    key = protocol["object.className"]
    print "parse_protocolqqq", key
    if key=="ProtImportMovies":
        parse_ProtImportMovies(protocol, acquisition2)
    elif key=="ProtMotionCorr":
        pass
    elif key=="ProtCTFFind":
        pass
    elif key=="ProtMonitorSummary":
        parse_ProtMonitorSummary(protocol, acquisition2)
