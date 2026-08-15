from database.db_manager import DatabaseManager


class CityModel:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def add(self, name: str):
        return self.db.execute("INSERT OR IGNORE INTO cities (name) VALUES (?)", (name.lower().strip(),))

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM cities ORDER BY name")

    def get_names(self):
        rows = self.db.fetch_all("SELECT name FROM cities ORDER BY name")
        return [r["name"] for r in rows]

    def delete(self, name: str):
        return self.db.execute("DELETE FROM cities WHERE name = ?", (name.lower().strip(),))

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

    def get_names(self):
        rows = self.db.fetch_all("SELECT name FROM niches ORDER BY name")
        return [r["name"] for r in rows]

    def get_unchecked(self):
        rows = self.db.fetch_all("SELECT * FROM niches WHERE is_checked = 0 ORDER BY name")
        return rows

    def get_unchecked_names(self):
        rows = self.db.fetch_all("SELECT name FROM niches WHERE is_checked = 0 ORDER BY name")
        return [r["name"] for r in rows]

    def set_checked(self, name: str, date: str = None):
        if date:
            return self.db.execute("UPDATE niches SET is_checked = 1, checked_date = ? WHERE name = ?", (date, name.strip()))
        return self.db.execute("UPDATE niches SET is_checked = 1 WHERE name = ?", (name.strip(),))

    def reset_checked(self, name: str):
        return self.db.execute("UPDATE niches SET is_checked = 0 WHERE name = ?", (name.strip(),))

    def delete(self, name: str):
        return self.db.execute("DELETE FROM niches WHERE name = ?", (name.strip(),))

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

    def add(self, domain, status, city, niche, date):
        return self.db.execute(
            "INSERT INTO domains (domain, status, city, niche, date) VALUES (?,?,?,?,?)",
            (domain, status, city.lower().strip(), niche.strip(), date),
        )

    def add_many(self, records: list):
        self.db.execute_many(
            "INSERT INTO domains (domain, status, city, niche, date) VALUES (?,?,?,?,?)",
            records,
        )

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM domains ORDER BY id DESC")

    def get_by_niche(self, niche: str):
        return self.db.fetch_all("SELECT * FROM domains WHERE niche = ? ORDER BY city", (niche,))

    def get_by_city(self, city: str):
        return self.db.fetch_all("SELECT * FROM domains WHERE city = ? ORDER BY niche", (city.lower().strip(),))

    def get_by_status(self, status: str):
        return self.db.fetch_all("SELECT * FROM domains WHERE status LIKE ? ORDER BY niche, city", (f"%{status}%",))

    def get_available(self):
        return self.db.fetch_all("SELECT * FROM domains WHERE status LIKE '%Available%' ORDER BY niche, city")

    def delete_by_city(self, city: str):
        return self.db.execute("DELETE FROM domains WHERE city = ?", (city.lower().strip(),))

    def delete_by_niche(self, niche: str):
        return self.db.execute("DELETE FROM domains WHERE niche = ?", (niche,))

    def count(self):
        result = self.db.fetch_one("SELECT COUNT(*) as cnt FROM domains")
        return result["cnt"] if result else 0

    def count_by_status(self):
        return self.db.fetch_all(
            "SELECT status, COUNT(*) as cnt FROM domains GROUP BY status"
        )


class NicheSummaryModel:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def upsert(self, niche, available, not_available, unknown, date):
        existing = self.db.fetch_one(
            "SELECT id FROM niche_summary WHERE niche = ?", (niche,)
        )
        if existing:
            self.db.execute(
                "UPDATE niche_summary SET available=?, not_available=?, unknown=?, date=? WHERE niche=?",
                (available, not_available, unknown, date, niche),
            )
        else:
            self.db.execute(
                "INSERT INTO niche_summary (niche, available, not_available, unknown, date) VALUES (?,?,?,?,?)",
                (niche, available, not_available, unknown, date),
            )

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM niche_summary ORDER BY niche")

    def get_by_niche(self, niche: str):
        return self.db.fetch_one("SELECT * FROM niche_summary WHERE niche = ?", (niche,))

    def delete_by_niche(self, niche: str):
        return self.db.execute("DELETE FROM niche_summary WHERE niche = ?", (niche,))

    def adjust_counts(self, niche, available_delta=0, not_available_delta=0, unknown_delta=0):
        existing = self.db.fetch_one(
            "SELECT available, not_available, unknown FROM niche_summary WHERE niche = ?",
            (niche,),
        )
        if not existing:
            return
        new_avail = max(0, existing["available"] + available_delta)
        new_reg = max(0, existing["not_available"] + not_available_delta)
        new_unk = max(0, existing["unknown"] + unknown_delta)
        self.db.execute(
            "UPDATE niche_summary SET available=?, not_available=?, unknown=? WHERE niche=?",
            (new_avail, new_reg, new_unk, niche),
        )
