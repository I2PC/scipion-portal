## Scipion Portal

> http://calm-shelf-73264.herokuapp.com

## Set up

### Configuration file: scipion.conf

The default location for the configuration file is `$HOME/.config/scipion-portal/scipion.conf`.
You can set the environment variable `SCIPION_CONF` to use a different path. See file `scipion.conf.template`
in the repository for reference.

### Database: postgreSQL

Set the environment variable `DATABASE_URL`. Example: `postgres://user:password@localhost:5432/scipion`.

## Test: Query from command line:

```
$ curl http://calm-shelf-73264.herokuapp.com/report_protocols/api/workflow/protocol/?name=ProtMonitorSystem<br>
$ curl http://calm-shelf-73264.herokuapp.com/report_protocols/api/workflow/workflow/?project_uuid=b9a2d873-53d2-42fb-aa69-a5002f2f08e9
```

### Downloads

Files in section _Download_ are stored in `static/install` and its contents described by the file
`static/install/downloadables.json`. See `static/install/downloadables.json.template` in the repository
for reference.

## Admin interface (requires password)

> http://calm-shelf-73264.herokuapp.com/admin/

## Details of usage data collection

You can find them here https://github.com/I2PC/scipion/wiki/Collecting-Usage-Statistics-for-Scipion

## Convert old sqlite3 database to postgres

Install the dependencies:

```
$ sudo pip install records
```

And execute the utilities script passing source and target database path/url. An example:

```
$ python utilities/convert_db_sqlite_to_postgres.py \
  downloads.sqlite3 \
  postgres://user:password@localhost:5432/scipion
```
