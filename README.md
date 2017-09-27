

## Scipion Portal

> http://calm-shelf-73264.herokuapp.com
> http://scipion.i2pc.es

## Set up

### Dependencies

```
$ sudo pip install -r requirements.txt
```

### Configuration file: scipion.conf

The default location for the configuration file is `$HOME/.config/scipion-portal/scipion.conf`.
Use the environment variable `SCIPION_CONFIG` for a different path. See file `scipion.conf.template`
in the repository for reference.

## Development server

```
$ export SCIPION_CONFIG=path/to/scipion.conf
$ export DATABASE_URL=postgres://user:password@localhost:5432/scipion
$ python manage.py runserver
```

### Downloads

Files in section _Download_ are stored in `static/install` and its contents described by the file
`static/install/downloadables.json`. See `static/install/downloadables.json.template` in the repository
for reference.

### Database: Postgres

```
$ createdb scipion
$ pg_restore scipion_usage_bd_20170620.backup | psql scipion
$ psql scipion
$ echo "ALTER TABLE django_content_type ADD COLUMN name character varying(50) NOT NULL DEFAULT 'someName';" | psql scipion
```

Set the environment variable `DATABASE_URL`. Example: `postgres://user:password@localhost:5432/scipion`.
```
$ export DATABASE_URL=postgres://user:password@localhost:5432/scipion
$ python manage.py migrate --fake-initial
```

## Database: Convert old sqlite3 database to postgres

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

## Admin interface (requires password)

> http://scipion.i2pc.es/admin/

## Details of usage data collection

You can find them here https://github.com/I2PC/scipion/wiki/Collecting-Usage-Statistics-for-Scipion

## Test: Query from command line:

```
$ curl http://scipion.i2pc.es/report_protocols/api/workflow/protocol/?name=ProtMonitorSystem<br>
$ curl http://scipion.i2pc.es/report_protocols/api/workflow/workflow/?project_uuid=b9a2d873-53d2-42fb-aa69-a5002f2f08e9
```
