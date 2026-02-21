import sqlite3

conn = sqlite3.connect('backend/db/vault.db')

with open('backend/db/schema.sql', 'r') as f:
  file = f.read()

conn.executescript(file)
conn.commit()
conn.close()