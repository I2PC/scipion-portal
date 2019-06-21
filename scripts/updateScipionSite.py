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
import base64
import json
import os
import sys

from pyworkflow.install.plugin_funcs import PluginRepository
from pyworkflow.project import Manager
from pyworkflow.em import Domain

GITHUB_COM = "github.com/"

gitHubCli = None


def usage(error):
    print ("""
    ERROR: %s

    Usage: scipion python .../updatePackages.py

        This script will generate a json output tha can be use at 
        {{server}}/report_protocols/api/workflow/package/updatecollaborators/ in the body
        of a POST request 
    """ % error)
    sys.exit(1)


def jsonEscape(str):
    return str.replace("\n", "");

def askForInput(msg, default=None, encrypt=False):

    if not encrypt:
        value = raw_input(msg)
    else:
        from getpass import getpass
        value = getpass(msg)

    if not value:
        value = default

    return value

def getEnvVariable(name, default=None, ask=False, encrypt=False):

    value = os.environ.get(name, None)

    if not value and ask:
        value = askForInput(name + ": ", default, encrypt)
        os.environ[name] = value

    return value

def getGitHubCli():

    global gitHubCli

    if not gitHubCli:

        from github import Github

        # Get credentials:
        user = getEnvVariable("GITHUB_USER", None, ask=True)
        password = getEnvVariable("GITHUB_PASS", None, ask=True, encrypt=True)

        gitHubCli = Github(user, password)

    return gitHubCli


def getGithubCollaborations(githuburl):
    print("Plugin home page is %s" % githuburl)

    # If it is a github page
    if not GITHUB_COM in githuburl:
        return []

    else:

        g = getGitHubCli()

        repo = g.get_repo(githuburl.split(GITHUB_COM)[1])
        return repo.get_stats_contributors()


def sendJsonToScipionSite(url, data):

    # Prepare the request
    import urllib2
    siteUrl = os.environ.get("SCIPION_SITE_URL", "http://127.0.0.1:8000")

    reqUrl = "/".join([siteUrl, url])

    print ("Sending data to " + reqUrl)
    req = urllib2.Request(reqUrl)
    req.add_header('Content-Type', 'application/json')

    # Authentication
    # Get credentials
    user = getEnvVariable("SCIPION_SITE_USER", None, ask=True)
    password = getEnvVariable("SCIPION_SITE_PASS", None, ask=True, encrypt=True)

    if user:

        base64string = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)

    # Data to json
    dataJson = json.dumps(data)
    response = urllib2.urlopen(req, dataJson)
    print ("Data sent to: " + reqUrl)

def updateCollaborators():

    """
    Need to generate this structure
       [
          {"package": "package1",
           "githubName": "octouser1",
           "name": "John Smith",
           "url": "-->github user url"
           "image": "avatar url"},
          ...
       ]
    """

    packages = [{"name": "scipion",
             "url": "https://github.com/I2PC/scipion",
             "description": ""}
            ]

    for name, plugin in PluginRepository().getPlugins().iteritems():
        try:
            pluginDict = {}
            pluginDict["name"]=plugin.getDirName()
            pluginDict["url"]=plugin.getHomePage()
            pluginDict["description"] = plugin.getSummary()
            packages.append(pluginDict)

        except Exception as e:
            print ("Couldn't get info from %s: %s " % (name, e))

    # Update packages
    sendJsonToScipionSite("report_protocols/api/v2/package/batchupdate/",
                          packages)

    for package in packages:
        try:
            name = package["name"]
            url = package["url"]
            collabs = []
            collaborations = getGithubCollaborations(url)
            for collaboration in collaborations:
                collabJson = dict()
                collabJson["package"] = name
                collabJson["packageurl"] = url
                collabJson["githubName"] = collaboration.author.login
                collabJson["name"] = collaboration.author.login
                collabJson["url"] = collaboration.author.html_url
                collabJson["image"] = collaboration.author.avatar_url

                collabs.append(collabJson)

            sendJsonToScipionSite("report_protocols/api/v2/package/updatecollaborators/", collabs)
        except Exception as e:
            print(e)
            print ("Failed to extract info from %s." % name)

def updateProtocols():

    prots = Domain.getProtocols()

    """
    Need to generate this structure
    [
      {"name": "prot1", "description": "this protocol ....", "friendlyName": "nice name", "package": "packageB"},
      {"name": "prot2", "description": "this protocol2 ....", "friendlyName": "nice name2", "package": "packageA"}
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
            if not prot.isBase():
                protOut["name"] = className
                protOut["friendlyName"] = str(prot.getClassLabel(prependPackageName=False))
                protOut["description"] = jsonEscape(prot.getHelpText())
                protOut["package"] = prot.getClassPackageName()
                protsOut.append(protOut)

        except Exception as e:
            print ("%s failed to be printed." % className)

    sendJsonToScipionSite("report_protocols/api/v2/protocol/batchupdate/", protsOut)


######## Execution lines ######

n = len(sys.argv)

if n > 2:
    usage("Incorrect number of input parameters")


# Actual call to update site
updateProtocols()

updateCollaborators()