import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_data.db")


class DatabaseManager:
    """SQLite access that is safe to use from multiple threads.

    Each operation opens its own short-lived connection and closes it in a
    ``finally`` block, so a connection is never shared across (or used from)
    another thread. This avoids the previous race where a single
    ``self.connection`` attribute was overwritten and closed by concurrent
    threads.
    """

    def __init__(self):
        self.db_path = DB_PATH

    def connect(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        conn = self.connect()
        try:
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

            # Indexes for the GROUP BY / filter queries used across the app.
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_domains_city ON domains (city)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_domains_niche ON domains (niche)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_domains_status ON domains (status)")

            conn.commit()
        finally:
            conn.close()

    def migrate(self):
        conn = self.connect()
        try:
            cursor = conn.cursor()
            for table, column in (("cities", "ignore_it"), ("niches", "ignore_it")):
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} INTEGER DEFAULT 0")
                except Exception:
                    pass
            # Legacy denormalized table: all statistics are now derived live
            # from the ``domains`` table, so drop it on existing databases.
            cursor.execute("DROP TABLE IF EXISTS niche_summary")
            conn.commit()
        finally:
            conn.close()

    def execute(self, query, params=None, conn=None):
        own = conn is None
        if own:
            conn = self.connect()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if own:
                conn.commit()
            return cursor.lastrowid
        finally:
            if own:
                conn.close()

    def fetch_all(self, query, params=None):
        conn = self.connect()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def fetch_one(self, query, params=None):
        conn = self.connect()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def execute_many(self, query, data_list, conn=None):
        own = conn is None
        if own:
            conn = self.connect()
        try:
            conn.executemany(query, data_list)
            if own:
                conn.commit()
        finally:
            if own:
                conn.close()

    @contextmanager
    def transaction(self):
        """Run several statements as one atomic transaction.

        Yields a connection (same ``sqlite3.Row`` factory as the ``fetch_*``
        helpers). Commits when the block succeeds, rolls back on any
        exception, and always closes the connection. Pass the yielded
        connection to ``execute``/``execute_many`` or model methods via their
        ``conn`` argument so every statement shares the same transaction.
        """
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
