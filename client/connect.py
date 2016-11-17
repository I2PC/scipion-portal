#!/usr/bin/env python
import urllib
import urllib2
import threading
#hashlib.sha256()
#url='http://localhost:8000/'
def connect():
    url='https://secret-reaches-65198.herokuapp.com/'
    webserver = 'report_protocols/api/workflow/workflow/addOrUpdateWorkflow/'
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
    data = urllib.urlencode({'hash':"myhash",
                             'json':"myjson"})
    content = opener.open(url+ webserver, data=data).read()
    print content

t = threading.Thread(target=connect)
t.start() # will execute func in a separate thread

#t.join() # will wait for spawned thread to die