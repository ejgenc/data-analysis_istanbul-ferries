import os
from pathlib import Path

# --- delete db files if they already exist ---
db_files = {"istanbul-ferries-db.sqlite3", "istanbul-ferries-dump.txt"}
db_path = Path("data/db/")

for filename in os.listdir(db_path):
    print(filename)
    if filename in db_files:
        try:
            os.unlink(os.path.join(db_path, filename))
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (filename, e))
