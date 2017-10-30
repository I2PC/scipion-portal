#!/usr/bin/python
"""
Convert a sqlite DB with download info to Postgres table.

Dependencies:

    $ sudo pip install records

Usage example:

    $ python convert_db_sqlite_to_postgres.py \
        downloads.sqlite3 \
        postgres://user@password:localhost:5432/scipion
"""
from __future__ import print_function
import sys
import os

import records

COLUMNS = [
    "creation", "fullName", "organization", "email",
    "subscription", "country", "version", "platform",
]

def debug(line):
    """Print line to stderr."""
    print(line, file=sys.stderr)

def get_source_objects(source):
    """Return iterable containing source rows as dicts."""
    classes = source.query("select * from Classes")
    columns_mapping = dict((class_.column_name, class_.label_property) for class_ in classes)
    debug("columns mapping: {}".format(columns_mapping))
    objects_with_classes_as_headers = source.query('select * from Objects')
    for obj in objects_with_classes_as_headers:
        if obj.enabled == 1:
            yield dict((columns_mapping.get(col, col), val) for (col, val) in obj.as_dict().items())

def get_count(database, table):
    """Return number of rows for a table."""
    return database.query("SELECT COUNT(*) as count FROM {table}".format(table=table))[0].count

def insert_objects(target, objects):
    """Insert iterable of objects (row as dictionary) to target DB."""
    insert_query = """
        INSERT INTO
            web_download ({columns})
        SELECT
            {values}
        WHERE NOT EXISTS
            (SELECT 1 FROM web_download WHERE ({columns}) = ({values}))
    """.format(
        columns=",".join('"{}"'.format(column) for column in COLUMNS),
        values=",".join(":" + column for column in COLUMNS),
    )
    count_before = get_count(target, "web_download")
    for obj in objects:
        target.query(insert_query, **obj)
    count_after = get_count(target, "web_download")
    return count_after - count_before

def sqlite3_to_postgres(source_sqlite3_path, target_postgres_url):
    """Convert sqlite3 DB to postgres."""
    debug("source: {}".format(source_sqlite3_path))
    debug("target: {}".format(target_postgres_url))
    source = records.Database("sqlite:///" + source_sqlite3_path)
    target = records.Database(target_postgres_url)

    objects = list(get_source_objects(source))
    inserted_count = insert_objects(target, objects)
    debug("Inserted: {} rows".format(inserted_count))

def main(args):
    """Process arguments to sqlite3_to_postgres."""
    if len(args) != 2:
        name = os.path.basename(sys.argv[0])
        print("Usage: {} SOURCE_SQLITE_PATH TARGET_POSTGRES_URL".format(name), file=sys.stderr)
        return 1
    else:
        source_sqlite3_path, target_postgres_url = args
        sqlite3_to_postgres(source_sqlite3_path, target_postgres_url)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
