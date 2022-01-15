from pathlib import Path
import sqlite3

# --- Create connection with the database ---
# connect
db_path = Path("data/db/istanbul-ferries-db.sqlite3")
conn = sqlite3.connect("test")
# set up db
cursor = conn.cursor()
# list to hold all queries
sql_queries = []


# --- Create tables in the database ---
# test query
query = """
CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY,
                   title TEXT, author TEXT, price TEXT, year TEXT)
"""
sql_queries.append(query)


# --- Execute and commit all SQL queries ---
for query in sql_queries:
    cursor.execute(query)
    conn.commit()
