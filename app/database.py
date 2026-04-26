import sqlite3
import os

DB_PATH = "disasterroute.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shelters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER,
            name TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            capacity INTEGER NOT NULL,
            current_occupancy INTEGER DEFAULT 0,
            FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evacuations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER,
            origin_lat REAL,
            origin_lon REAL,
            shelter_id INTEGER,
            algorithm TEXT,
            distance REAL,
            duration REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_roads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER,
            node_from INTEGER,
            node_to INTEGER,
            FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
        )
    """)

    conn.commit()
    conn.close()