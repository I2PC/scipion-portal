# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************
"""
This modules serve to define some Configuration classes
mainly for project GUI
"""

import os
from collections import OrderedDict
from ConfigParser import ConfigParser

def loadEmailConf(confFile):
    """ Load configuration parameters to be used for emailing.
    By default read from: scipion.conf
    """
    # Read menus from users' config file.
    cp = ConfigParser()
    cp.optionxform = str  # keep case (stackoverflow.com/questions/1611799)
    emailConf = OrderedDict()

    assert cp.read(confFile) != [], 'Missing file %s' % confFile

    # Set options from EMAIL main section
    def setm(option, default):
        if cp.has_option('EMAIL', option):
            emailConf[option] = cp.get('EMAIL', option)
        else:
            emailConf[option] = default

    setm('EMAIL_HOST', 'localhost')
    setm('EMAIL_PORT', '25')
    setm('EMAIL_HOST_USER', 'smtpuser')
    setm('EMAIL_HOST_PASSWORD', 'smtppassword')
    setm('EMAIL_USE_TLS', False)

    setm('EMAIL_FOR_SUBSCRIPTION', 'scipion-users-join@lists.sourceforge.net')

    return emailConf