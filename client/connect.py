#!/usr/bin/env python
import urllib
import urllib2
import threading
import uuid

def connect():
    #check if there is a saved uuid
    #if not generate one with uuid.uuid4()
    #export workflow
    #export DATABASE_URL='postgres://alumnodb:alumnodb@localhost/scipion'


    #then connect to webserver a send json
    url='http://calm-shelf-73264.herokuapp.com/'
    webserver = 'report_protocols/api/workflow/workflow/addOrUpdateWorkflow/'
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
    data = urllib.urlencode({'project_uuid':"myproject_uuid",
                             'project_workflow':"myproject_workflow"})
    content = opener.open(url+ webserver, data=data).read()
    print content


#check in config if report is on
t = threading.Thread(target=connect)
t.start() # will execute function in a separate thread

#t.join() # will wait for spawned thread to die