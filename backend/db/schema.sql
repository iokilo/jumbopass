CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  password_salt TEXT NOT NULL,
  kdf_params TEXT NOT NULL,
  rfid_val TEXT
)

CREATE TABLE vault_entries (
  entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  url TEXT NOT NULL,
  notes TEXT,
  last_updated TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
  created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
  FOREIGN KEY (user_id) REFERENCES users (user_id),
)