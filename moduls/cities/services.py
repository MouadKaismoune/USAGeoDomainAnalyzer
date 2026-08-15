import time
import requests
from datetime import datetime
from database import db
from database.models import CityModel, NicheSummaryModel

model = CityModel(db)
summary_model = NicheSummaryModel(db)

RUNNING = True


def stop_add_city():
    global RUNNING
    RUNNING = False


def check_domain_rdap(domain):
    url = f"https://rdap.verisign.com/com/v1/domain/{domain}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return "❌ Registered"
        elif response.status_code == 404:
            return "✅ Available"
        else:
            return f"⚠️ Unknown ({response.status_code})"
    except Exception:
        return "⚠️ Error"


def get_all_cities():
    return model.get_all()


def get_city_names():
    return model.get_names()


def set_city_ignore(name: str, value: bool):
    model.set_ignore(name, value)


def get_ignored_city_names():
    rows = db.fetch_all("SELECT name FROM cities WHERE ignore_it = 1")
    return {r["name"].lower() for r in rows}


def add_city(name: str, progress_callback=None) -> tuple:
    global RUNNING
    RUNNING = True

    if model.exists(name):
        return False, "already_exists"

    city = name.strip().lower()
    model.add(city)

    date_today = datetime.today().strftime("%d-%m-%Y")

    checked_niches = db.fetch_all(
        "SELECT name FROM niches WHERE is_checked = 1 ORDER BY name"
    )

    if not checked_niches:
        return True, "added_success"

    niche_counters = {}
    all_records = []

    for niche_row in checked_niches:
        if not RUNNING:
            break

        niche = niche_row["name"]
        niche_counters[niche] = {"available": 0, "not_available": 0, "unknown": 0}

        domain = f"{city}{niche}.com"
        status = check_domain_rdap(domain)

        all_records.append((domain, status, city, niche, date_today))

        status_lower = status.lower()
        if "available" in status_lower and "registered" not in status_lower:
            niche_counters[niche]["available"] += 1
        elif "registered" in status_lower:
            niche_counters[niche]["not_available"] += 1
        else:
            niche_counters[niche]["unknown"] += 1

        if progress_callback:
            progress_callback(
                domain=domain,
                status=status,
                niche=niche,
            )

        time.sleep(2)

    if all_records:
        db.execute_many(
            "INSERT INTO domains (domain, status, city, niche, date) VALUES (?,?,?,?,?)",
            all_records,
        )

    for niche, counts in niche_counters.items():
        existing = db.fetch_one(
            "SELECT * FROM niche_summary WHERE niche = ?", (niche,)
        )
        if existing:
            new_avail = existing["available"] + counts["available"]
            new_notavail = existing["not_available"] + counts["not_available"]
            new_unknown = existing["unknown"] + counts["unknown"]
            db.execute(
                "UPDATE niche_summary SET available=?, not_available=?, unknown=?, date=? WHERE niche=?",
                (new_avail, new_notavail, new_unknown, date_today, niche),
            )
        else:
            db.execute(
                "INSERT INTO niche_summary (niche, available, not_available, unknown, date) VALUES (?,?,?,?,?)",
                (niche, counts["available"], counts["not_available"], counts["unknown"], date_today),
            )

    return True, "added_success"


def delete_city(name: str) -> tuple:
    if not model.exists(name):
        return False, "not_found"
    city = name.strip().lower()

    removed = db.fetch_all(
        "SELECT niche, status FROM domains WHERE city = ?", (city,)
    )
    removed_counts = {}
    for row in removed:
        niche = row["niche"]
        status = row["status"].lower()
        if niche not in removed_counts:
            removed_counts[niche] = {"avail": 0, "notavail": 0, "unknown": 0}
        if "available" in status and "registered" not in status:
            removed_counts[niche]["avail"] += 1
        elif "registered" in status:
            removed_counts[niche]["notavail"] += 1
        else:
            removed_counts[niche]["unknown"] += 1

    db.execute("DELETE FROM domains WHERE city = ?", (city,))

    for niche, counts in removed_counts.items():
        existing = db.fetch_one(
            "SELECT * FROM niche_summary WHERE niche = ?", (niche,)
        )
        if existing:
            new_avail = max(0, existing["available"] - counts["avail"])
            new_notavail = max(0, existing["not_available"] - counts["notavail"])
            new_unknown = max(0, existing["unknown"] - counts["unknown"])
            db.execute(
                "UPDATE niche_summary SET available=?, not_available=?, unknown=? WHERE niche=?",
                (new_avail, new_notavail, new_unknown, niche),
            )

    model.delete(city)
    return True, "deleted_success"


def get_city_count():
    return model.count()


def get_city_stats(city: str):
    rows = db.fetch_all(
        "SELECT status, COUNT(*) as cnt FROM domains WHERE city = ? GROUP BY status",
        (city.lower().strip(),),
    )
    stats = {"available": 0, "registered": 0, "unknown": 0}
    total = 0
    for row in rows:
        s = row["status"].lower()
        c = row["cnt"]
        total += c
        if "available" in s and "registered" not in s:
            stats["available"] = c
        elif "registered" in s:
            stats["registered"] = c
        else:
            stats["unknown"] += c

    registered_pct = round((stats["registered"] / total * 100), 2) if total > 0 else 0
    return {
        "available": stats["available"],
        "registered": stats["registered"],
        "unknown": stats["unknown"],
        "total": total,
        "registered_pct": registered_pct,
    }


def get_all_cities_with_stats():
    cities = get_all_names_with_ids()
    result = []
    for city in cities:
        stats = get_city_stats(city["name"])
        result.append({
            "id": city["id"],
            "name": city["name"],
            "ignore_it": city["ignore_it"],
            "available": stats["available"],
            "registered": stats["registered"],
            "unknown": stats["unknown"],
            "total": stats["total"],
            "strength": stats["registered_pct"],
        })
    return result


def get_all_names_with_ids():
    return db.fetch_all("SELECT id, name, ignore_it FROM cities ORDER BY name")
