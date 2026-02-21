import sqlite3

conn = sqlite3.connect('vault.db')

with open('schema.sql', 'r') as f:
  conn.executescript(f.read())

conn.commit()
conn.close()