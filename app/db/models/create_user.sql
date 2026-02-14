CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    balance INTEGER NOT NULL DEFAULT 0,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    goal TEXT,
    created_at TEXT);