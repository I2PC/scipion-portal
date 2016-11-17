#!/usr/bin/env python
import urllib
import urllib2
#hashlib.sha256()
url='http://localhost:8000/report_protocols/api/workflow/workflow/addOrUpdateWorkflow/'
opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
data = urllib.urlencode({'hash':"myhash",
                         'json':"myjson"})
content = opener.open(url,data=data).read()
print content