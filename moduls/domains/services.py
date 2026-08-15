from database import db
from database.models import DomainModel

model = DomainModel(db)


def get_all_domains():
    return model.get_all()


def get_domains_by_niche(niche: str):
    return model.get_by_niche(niche)


def get_domains_by_city(city: str):
    return model.get_by_city(city)


def get_available_domains():
    return model.get_available()


def get_domain_count():
    return model.count()


def get_status_counts():
    counts = model.count_by_status()
    result = {"available": 0, "registered": 0, "unknown": 0}
    for row in counts:
        status = row["status"].lower()
        if "available" in status:
            result["available"] = row["cnt"]
        elif "registered" in status:
            result["registered"] = row["cnt"]
        else:
            result["unknown"] += row["cnt"]
    return result


def add_domain(domain, status, city, niche, date):
    return model.add(domain, status, city, niche, date)


def add_domains_bulk(records: list):
    model.add_many(records)


def delete_domains_by_city(city: str):
    return model.delete_by_city(city)


def delete_domains_by_niche(niche: str):
    return model.delete_by_niche(niche)


def _get_active_domains():
    domains = model.get_all()
    if not domains:
        return []
    ignored_cities = {r["name"].lower() for r in db.fetch_all("SELECT name FROM cities WHERE ignore_it = 1")}
    ignored_niches = {r["name"] for r in db.fetch_all("SELECT name FROM niches WHERE ignore_it = 1")}
    return [
        d for d in domains
        if d["city"].lower() not in ignored_cities
        and d["niche"] not in ignored_niches
    ]


def _compute_registered_pct(active, group_col):
    totals = {}
    registered = {}
    for d in active:
        key = d[group_col]
        if group_col == "city":
            key = key.lower()
        status = d["status"].lower()
        totals[key] = totals.get(key, 0) + 1
        if "registered" in status:
            registered[key] = registered.get(key, 0) + 1
    result = {}
    for key in totals:
        t = totals[key]
        r = registered.get(key, 0)
        result[key] = round((r / t * 100), 2) if t > 0 else 0
    return result


def get_all_domains_with_strength():
    active = _get_active_domains()
    if not active:
        return []

    city_pcts = _compute_registered_pct(active, "city")
    niche_pcts = _compute_registered_pct(active, "niche")

    result = []
    for d in active:
        city = d["city"]
        niche = d["niche"]
        city_pct = city_pcts.get(city.lower(), 0)
        niche_pct = niche_pcts.get(niche, 0)
        strength = round((city_pct + niche_pct) / 2, 2)

        result.append({
            "id": d["id"],
            "domain": d["domain"],
            "status": d["status"],
            "city": d["city"],
            "niche": d["niche"],
            "date": d["date"],
            "city_strength": city_pct,
            "niche_strength": niche_pct,
            "strength": strength,
        })

    return result
