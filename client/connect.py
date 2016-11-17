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
    url='https://secret-reaches-65198.herokuapp.com/'
    webserver = 'report_protocols/api/workflow/workflow/addOrUpdateWorkflow/'
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
    data = urllib.urlencode({'hash':"myhash",
                             'json':"myjson"})
    content = opener.open(url+ webserver, data=data).read()
    print content


#check in config if report is on
t = threading.Thread(target=connect)
t.start() # will execute function in a separate thread

#t.join() # will wait for spawned thread to die