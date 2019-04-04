#!/usr/bin/env python
# **************************************************************************
# *
# * Authors:     Pablo Conesa (pconesa@cnb.csic.es)
# *
# * Unidad de Bioinformatica of Centro Nacional de Biotecnologia, CSIC
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
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import sys

from pyworkflow.em import Domain
from pyworkflow.project import Manager
import json

def usage(error):
    print ("""
    ERROR: %s

    Usage: scipion python .../updateProtocols.py

        This script will generate a json output tha can be use at 
        {{server}}/report_protocols/api/workflow/protocol/update/ in the body
        of a POST request 
    """ % error)
    sys.exit(1)


def jsonEscape(str):
    return str.replace("\n", "");


n = len(sys.argv)

if n > 2:
    usage("Incorrect number of input parameters")

# Create a new project
manager = Manager()

prots = Domain.getProtocols()

"""
Need to generate this structure
[
  {"name": "prot1", "description": "this protocol ....", "friendlyName": "nice name"},
  {"name": "prot2", "description": "this protocol2 ....", "friendlyName": "nice name2"}
  ...
]
"""
protsOut = []
for className in prots:

    try:
        protOut = dict()

        protClass = prots[className]
        # Instantiate it
        prot = protClass()
        protOut["name"] = className
        protOut["friendlyName"] = str(prot.getClassLabel())
        protOut["description"] = jsonEscape(prot.getHelpText())
        protsOut.append(protOut)
    except Exception as e:
        print ("%s failed to be printed." % className)

# Print it as json to the output


print (protsOut)
protsJson = json.dumps(protsOut)
print("\n\n")
print(protsJson)
