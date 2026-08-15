import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_data.db")


class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()

    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                ignore_it INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS niches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                is_checked INTEGER DEFAULT 0,
                checked_date TEXT DEFAULT NULL,
                ignore_it INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                status TEXT NOT NULL,
                city TEXT NOT NULL,
                niche TEXT NOT NULL,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS niche_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT UNIQUE NOT NULL,
                available INTEGER DEFAULT 0,
                not_available INTEGER DEFAULT 0,
                unknown INTEGER DEFAULT 0,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        self.close()

    def migrate(self):
        conn = self.connect()
        cursor = conn.cursor()
        for table, column in (("cities", "ignore_it"), ("niches", "ignore_it")):
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} INTEGER DEFAULT 0")
            except Exception:
                pass
        conn.commit()
        self.close()

    def execute(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        last_id = cursor.lastrowid
        self.close()
        return last_id

    def fetch_all(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        self.close()
        return results

    def fetch_one(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        row = cursor.fetchone()
        self.close()
        return dict(row) if row else None

    def execute_many(self, query, data_list):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executemany(query, data_list)
        conn.commit()
        self.close()
