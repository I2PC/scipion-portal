import dj_database_url

D = dj_database_url.config()

#set databae variables
print """export PGUSER=%s
export PGPASSWORD=%s
export PGHOST=%s
export PGDATABASE=%s
"""%(D['USER'],
     D['PASSWORD'],
     D['HOST'],
     D['NAME'])

#drop tables
print """
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
COMMENT ON SCHEMA public IS 'standard public schema';
"""
print """
select 'drop table "' || tablename || '" cascade;'
from pg_tables where schemaname = 'public';
"""
###select 'drop table "' || tablename || '" cascade;' from pg_tables;
