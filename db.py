import sqlite3
from globalSettings import *

dbName = DBPath

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.text_factory = str
        return conn
    except Exception as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)
    
    finally:
        conn.close()

create_table_sql = '''
CREATE TABLE IF NOT EXISTS `songs` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`path`	TEXT,
	`genre`	TEXT,
	`prediction`	INTEGER,
	`song`	TEXT
);
'''
create_table_sql2 = '''
CREATE TABLE IF NOT EXISTS `folder_paths` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`path`	TEXT
);
'''

conn = create_connection(dbName)
create_table(conn, create_table_sql)
conn = create_connection(dbName)
create_table(conn, create_table_sql2)