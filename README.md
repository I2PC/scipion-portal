## Shortcut to this page
 > http://tinyurl.com/scipion-readme

## See Protocol Usage Summary
> http://calm-shelf-73264.herokuapp.com/report_protocols/protocolTable/
> ( http://tinyurl.com/scipion-protocols )

## Activate
 Add the following two lines to Config ($HOME/.config/scipion/scipion.conf), section VARIABLES:

> SCIPION_NOTIFY = True<br>
> SCIPION_NOTIFY_URL = http://tinyurl.com/scipion-collect-potocols
-------------------------------------------------------------------------------------------------
\#http://calm-shelf-73264.herokuapp.com/report_protocols/api/workflow/workflow/<br>
\#SCIPION_NOTIFY_SECONDS = [Default to 3600*24 seconds= 1 day]


## Test: Query from command line:

> curl http://calm-shelf-73264.herokuapp.com/report_protocols/api/workflow/protocol/?name=ProtMonitorSystem<br>
> curl http://calm-shelf-73264.herokuapp.com/report_protocols/api/workflow/workflow/?project_uuid=b9a2d873-53d2-42fb-aa69-a5002f2f08e9

##Admin interface (requires password)

> http://calm-shelf-73264.herokuapp.com/admin/
