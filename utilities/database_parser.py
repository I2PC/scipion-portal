import dj_database_url

D = dj_database_url.config()

#set database variables
print """export PGUSER=%s
export PGPASSWORD=%s
export PGHOST=%s
export PGDATABASE=%s
"""%(D['USER'],
     D['PASSWORD'],
     D['HOST'],
     D['NAME'])
