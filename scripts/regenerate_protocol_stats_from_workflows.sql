delete from report_protocols_protocol;

INSERT INTO report_protocols_protocol (name, "timesUsed")
select protocol, count(*) from (
select unnest(
	string_to_array(
	 replace(
	  replace(
	   replace(
	    replace(project_workflow,', ',',')
	   ,'"','')
	  ,']','')
	 ,'[','')
        ,',')
        ) as protocol
from report_protocols_workflow) prot_list
group by protocol;