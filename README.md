## Scipion Portal

> http://calm-shelf-73264.herokuapp.com

> http://scipion.i2pc.es

## Set up

### Dependencies

```
$ cd scipion-portal
$ virtualenv --python /usr/bin/python2 env
$ env/bin/pip install -r requirements.txt
```

### Configuration file: scipion.conf. Only used for the email configuration

The default location for the configuration file is `$HOME/.config/scipion-portal/scipion.conf`.
Use the environment variable `SCIPION_CONFIG` for a different path. See file `scipion.conf.template`
in the repository for reference.

## Development server

```
$ export SCIPION_CONFIG=path/to/scipion.conf
$ export DATABASE_URL=postgres://user:password@localhost:5432/scipion
$ env/bin/python manage.py runserver
```

## Production server (Apache)

```
<VirtualHost *:80>
  ServerName scipion.i2pc.es
  Alias /static /home/ubuntu/scipion-portal/staticfiles

  <Directory /home/ubuntu/scipion-portal/staticfiles>
    Require all granted
  </Directory>

  <Directory /home/ubuntu/scipion-portal/main>
    <Files wsgi.py>
      Require all granted
    </Files>
  </Directory>

  WSGIDaemonProcess scipion-portal python-home=/home/ubuntu/scipion-portal/env python-path=/home/ubuntu/scipion-portal
  WSGIProcessGroup scipion-portal
  WSGIScriptAlias / /home/ubuntu/scipion-portal/main/wsgi.py

  SetEnv SCIPION_CONFIG /home/ubuntu/.config/scipion-portal/scipion.conf
  SetEnv DATABASE_URL postgres://scipion:j6rUtd8Y6qW@localhost:5432/scipion
</VirtualHost>
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
$ env/bin/pip install records
```

And execute the utilities script passing source and target database path/url. An example:

```
$ env/bin/python utilities/convert_db_sqlite_to_postgres.py \
  downloads.sqlite3 \
  postgres://user:password@localhost:5432/scipion
```

## Admin interface (requires password)

> http://scipion.i2pc.es/admin/

## Details of usage data collection

You can find them here https://github.com/I2PC/scipion/wiki/Collecting-Usage-Statistics-for-Scipion

## Test: Query from command line:

```
$ curl http://scipion.i2pc.es/report_protocols/api/workflow/protocol/?name=ProtMonitorSystem
$ curl http://scipion.i2pc.es/report_protocols/api/workflow/workflow/?project_uuid=b9a2d873-53d2-42fb-aa69-a5002f2f08e9
```
