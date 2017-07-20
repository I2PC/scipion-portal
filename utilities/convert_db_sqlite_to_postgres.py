#!/usr/bin/python
#
# Dependencies:
#
# $ sudo pip install records
#
# Usage example:
#
# $ python convert_db_sqlite_to_postgres.py downloads.sqlite3 postgres://localhost:5432/scipion
#
from __future__ import print_function
import sys
import os

import records

COLUMNS = [
    "creation", "fullName", "organization", "email",
    "subscription", "country", "version", "platform",
]

def debug(line):
    print(line, file=sys.stderr)

def get_source_objects(source):
    classes = source.query('select * from Classes')
    columns_mapping = dict((class_.column_name, class_.label_property) for class_ in classes)
    debug("columns mapping: {}".format(columns_mapping))
    objects_with_classes_as_headers = source.query('select * from Objects')
    return [
        dict((columns_mapping.get(col, col), val) for (col, val) in obj.as_dict().items())
        for obj in objects_with_classes_as_headers if obj.enabled == 1
    ]

def insert_not_existing_objects(target, objects):
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
    counts_before = target.query("SELECT COUNT(*) as count FROM web_download")[0].count
    for obj in objects:
        target.query(insert_query, **obj)
    counts_after = target.query("SELECT COUNT(*) as count FROM web_download")[0].count
    return counts_after - counts_before

def sqlite3_to_postgres(source_sqlite3_path, target_postgres_url):
    debug("source: {}".format(source_sqlite3_path))
    debug("target: {}".format(target_postgres_url))
    source = records.Database("sqlite:///" + source_sqlite3_path)
    target = records.Database(target_postgres_url)

    objects = get_source_objects(source)
    inserted_count = insert_not_existing_objects(target, objects)
    debug("Inserted: {} rows".format(inserted_count))

def main(args):
    if len(args) != 2:
        name = os.path.basename(sys.argv[0])
        print("Usage: {} SOURCE_SQLITE_PATH TARGET_POSTGRES_URL".format(name), file=sys.stderr)
        return 1
    else:
        source_sqlite3_path, target_postgres_url = args
        sqlite3_to_postgres(source_sqlite3_path, target_postgres_url)
        return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
