import re
import time
from datetime import datetime
from database import db
from database.models import CityModel
from moduls.domains.rdap import check_domain_rdap, classify_status

model = CityModel(db)

# A city is concatenated with the niche to form "<city><niche>.com", so it must
# be a single valid DNS label (letters, digits, hyphens; no spaces or dots).
_VALID_CITY = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def get_city_names():
    return model.get_names()


def set_city_ignore(name: str, value: bool):
    model.set_ignore(name, value)


def add_city(name: str, progress_callback=None, should_stop=None) -> tuple:
    city = name.strip().lower()
    if not _VALID_CITY.match(city):
        return False, "invalid_name"

    if model.exists(city):
        return False, "already_exists"

    date_today = datetime.today().strftime("%d-%m-%Y")

    checked_niches = db.fetch_all(
        "SELECT name FROM niches WHERE is_checked = 1 ORDER BY name"
    )

    all_records = []
    stopped = False

    for niche_row in checked_niches:
        if should_stop is not None and should_stop():
            stopped = True
            break

        niche = niche_row["name"]

        domain = f"{city}{niche}.com"
        status = check_domain_rdap(domain)

        all_records.append((domain, status, city, niche, date_today))

        if progress_callback:
            progress_callback(
                domain=domain,
                status=status,
                niche=niche,
            )

        time.sleep(2)

    # Cancelling aborts the whole add: nothing is written, so a stopped or
    # interrupted run can never leave a city without its domains.
    if stopped:
        return False, "stopped"

    # City and its domains are written in a single transaction.
    with db.transaction() as conn:
        model.add(city, conn=conn)
        if all_records:
            db.execute_many(
                "INSERT INTO domains (domain, status, city, niche, date) VALUES (?,?,?,?,?)",
                all_records,
                conn=conn,
            )

    return True, "added_success"


def delete_city(name: str) -> tuple:
    if not model.exists(name):
        return False, "not_found"
    city = name.strip().lower()

    with db.transaction() as conn:
        db.execute("DELETE FROM domains WHERE city = ?", (city,), conn=conn)
        model.delete(city, conn=conn)
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
        c = row["cnt"]
        total += c
        stats[classify_status(row["status"])] += c

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
