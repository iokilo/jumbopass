import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'db/vault.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # lets you access columns by name like a dict
    return conn