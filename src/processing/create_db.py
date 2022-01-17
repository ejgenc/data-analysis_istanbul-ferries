import os
from pathlib import Path
import io
import sqlite3


import pandas as pd


# --- Create connection with the database ---
# connect
db_path = Path("data/db/istanbul-ferries-db.sqlite3")
conn = sqlite3.connect(db_path)
# set up db
cursor = conn.cursor()
# list to hold all queries
sql_queries = []

# --- Create tables in the database ---
# create the "ferry-terminals" table
query = """
CREATE TABLE IF NOT EXISTS "ferry-terminals" (
    "id"            INTEGER PRIMARY KEY NOT NULL,
    "terminal-name" TEXT,
    "shape-data"    BLOB
);
"""
sql_queries.append(query)

# create the "ferry-lines" table
query = """
CREATE TABLE IF NOT EXISTS "ferry-lines" (
    "id"         INTEGER PRIMARY KEY NOT NULL,
    "line-name"  TEXT,
    "shape-data" BLOB
);
"""
sql_queries.append(query)

# create the "terminals-lines" table
query = """
CREATE TABLE IF NOT EXISTS "terminals-lines" (
    "terminal-id"   INTEGER NOT NULL,
    "terminal-name" TEXT,
    "has-line"      TEXT,
    "line-id"       INTEGER
);
"""
sql_queries.append(query)

# create the "trips-per-ferry-line" table
query = """
CREATE TABLE IF NOT EXISTS "trips-per-ferry-line" (
    "year"      INTEGER,
    "line-name" TEXT PRIMARY KEY NOT NULL,
    "n-trips"   INTEGER
);
"""
sql_queries.append(query)

# create the "transportation-load" table
query = """
CREATE TABLE IF NOT EXISTS "transportation-load" (
    "day"          INTEGER,
    "month"        INTEGER,
    "year"         INTEGER,
    "hour"         INTEGER,
    "n-passengers" INTEGER
);
"""
sql_queries.append(query)

# create the "weather-sensors" table
query = """
CREATE TABLE IF NOT EXISTS "weather-sensors" (
    "id"          INTEGER PRIMARY KEY NOT NULL,
    "sensor-name" TEXT,
    "shape-data"  BLOB
);
"""
sql_queries.append(query)

# create the "weather-observations" table
query = """
CREATE TABLE IF NOT EXISTS "weather-observations" (
    "day"          INTEGER,
    "month"        INTEGER,
    "year"         INTEGER,
    "hour"         INTEGER,
    "avg-temp"     REAL,
    "avg-humidity" REAL,
    "avg-precip"   REAL,
    "avg-wind"     REAL,
    "avg-winddir"  REAL
);
"""
sql_queries.append(query)

# Execute and commit all SQL queries
for query in sql_queries:
    cursor.execute(query)
    conn.commit()

# Populate the tables
datasets_path = Path("data/cleaned/")
datasets = [
    "ferry-lines",
    "ferry-terminals",
    "terminals-lines",
    "trips-per-ferry-line",
    "transportation-load",
    "weather-sensors",
    "weather-observations",
]
for dataset in datasets:
    df = pd.read_csv(
        os.path.join(datasets_path, (dataset + ".csv")),
        sep=",",
        encoding="utf-8-sig",
    )
    df.to_sql(dataset, con=conn, if_exists="append", index=False)


# --- Create a data dump ---
dump_path = Path("data/db/istanbul-ferries-dump.sql")
with io.open(dump_path, "w", encoding="utf-8-sig") as f:
    for line in conn.iterdump():
        f.write("%s\n" % line)

# --- Close the cursor and the connection ---
cursor.close()
conn.close()
