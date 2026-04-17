#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/17
@Project: Gravix
@File: schema.py
@Author: Claude
@Software: PyCharm
@Desc: Database schema definitions
"""

# SQL Schema definitions for Gravix Chat Database

# Sessions table schema
SESSIONS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Messages table schema
MESSAGES_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);
"""

# Indexes for better query performance
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);",
    "CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity DESC);",
    "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);",
]

# Full table creation script
FULL_SCHEMA = SESSIONS_TABLE_SCHEMA + MESSAGES_TABLE_SCHEMA + "\n".join(INDEXES)
