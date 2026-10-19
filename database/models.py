from database.db_manager import DatabaseManager


class CityModel:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def add(self, name: str, conn=None):
        return self.db.execute("INSERT OR IGNORE INTO cities (name) VALUES (?)", (name.lower().strip(),), conn=conn)

    def get_names(self):
        rows = self.db.fetch_all("SELECT name FROM cities ORDER BY name")
        return [r["name"] for r in rows]

    def delete(self, name: str, conn=None):
        return self.db.execute("DELETE FROM cities WHERE name = ?", (name.lower().strip(),), conn=conn)

    def set_ignore(self, name: str, value: bool):
        return self.db.execute(
            "UPDATE cities SET ignore_it = ? WHERE name = ?",
            (1 if value else 0, name.lower().strip()),
        )

    def exists(self, name: str):
        result = self.db.fetch_one("SELECT 1 FROM cities WHERE name = ?", (name.lower().strip(),))
        return result is not None

    def count(self):
        result = self.db.fetch_one("SELECT COUNT(*) as cnt FROM cities")
        return result["cnt"] if result else 0


class NicheModel:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def add(self, name: str):
        return self.db.execute("INSERT OR IGNORE INTO niches (name, is_checked) VALUES (?, 0)", (name.strip(),))

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM niches ORDER BY name")

    def get_unchecked(self):
        rows = self.db.fetch_all("SELECT * FROM niches WHERE is_checked = 0 ORDER BY name")
        return rows

    def get_unchecked_names(self):
        rows = self.db.fetch_all("SELECT name FROM niches WHERE is_checked = 0 ORDER BY name")
        return [r["name"] for r in rows]

    def set_checked(self, name: str, date: str = None, conn=None):
        if date:
            return self.db.execute("UPDATE niches SET is_checked = 1, checked_date = ? WHERE name = ?", (date, name.strip()), conn=conn)
        return self.db.execute("UPDATE niches SET is_checked = 1 WHERE name = ?", (name.strip(),), conn=conn)

    def reset_checked(self, name: str, conn=None):
        return self.db.execute("UPDATE niches SET is_checked = 0 WHERE name = ?", (name.strip(),), conn=conn)

    def delete(self, name: str, conn=None):
        return self.db.execute("DELETE FROM niches WHERE name = ?", (name.strip(),), conn=conn)

    def set_ignore(self, name: str, value: bool):
        return self.db.execute(
            "UPDATE niches SET ignore_it = ? WHERE name = ?",
            (1 if value else 0, name.strip()),
        )

    def exists(self, name: str):
        result = self.db.fetch_one("SELECT 1 FROM niches WHERE LOWER(name) = LOWER(?)", (name.strip(),))
        return result is not None

    def count(self):
        result = self.db.fetch_one("SELECT COUNT(*) as cnt FROM niches")
        return result["cnt"] if result else 0

    def count_checked(self):
        result = self.db.fetch_one("SELECT COUNT(*) as cnt FROM niches WHERE is_checked = 1")
        return result["cnt"] if result else 0

    def count_unchecked(self):
        result = self.db.fetch_one("SELECT COUNT(*) as cnt FROM niches WHERE is_checked = 0")
        return result["cnt"] if result else 0


class DomainModel:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_many(self, records: list, conn=None):
        self.db.execute_many(
            "INSERT INTO domains (domain, status, city, niche, date) VALUES (?,?,?,?,?)",
            records,
            conn=conn,
        )

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM domains ORDER BY id DESC")

    def delete_by_niche(self, niche: str, conn=None):
        return self.db.execute("DELETE FROM domains WHERE niche = ?", (niche,), conn=conn)

    def count_by_status(self):
        return self.db.fetch_all(
            "SELECT status, COUNT(*) as cnt FROM domains GROUP BY status"
        )

