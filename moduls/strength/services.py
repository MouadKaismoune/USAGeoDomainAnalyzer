from database import db
from database.models import DomainModel

model = DomainModel(db)


def _get_ignored_sets():
    ignored_cities = {r["name"].lower() for r in db.fetch_all("SELECT name FROM cities WHERE ignore_it = 1")}
    ignored_niches = {r["name"] for r in db.fetch_all("SELECT name FROM niches WHERE ignore_it = 1")}
    return ignored_cities, ignored_niches


def calculate_domain_strength():
    all_domains = model.get_all()
    if not all_domains:
        return []

    ignored_cities, ignored_niches = _get_ignored_sets()

    active = [
        d for d in all_domains
        if d["city"].lower() not in ignored_cities
        and d["niche"] not in ignored_niches
    ]
    if not active:
        return []

    city_totals = {}
    city_registered = {}
    niche_totals = {}
    niche_registered = {}

    for d in active:
        city = d["city"].lower()
        niche = d["niche"]
        status = d["status"].lower()

        city_totals[city] = city_totals.get(city, 0) + 1
        niche_totals[niche] = niche_totals.get(niche, 0) + 1

        if "registered" in status:
            city_registered[city] = city_registered.get(city, 0) + 1
            niche_registered[niche] = niche_registered.get(niche, 0) + 1

    results = []
    for d in active:
        status = d["status"].lower()
        if "available" not in status or "registered" in status:
            continue

        city = d["city"].lower()
        niche = d["niche"]

        city_reg_pct = 0
        if city_totals.get(city, 0) > 0:
            city_reg_pct = round((city_registered.get(city, 0) / city_totals[city]) * 100, 2)

        niche_reg_pct = 0
        if niche_totals.get(niche, 0) > 0:
            niche_reg_pct = round((niche_registered.get(niche, 0) / niche_totals[niche]) * 100, 2)

        total_score = round((city_reg_pct + niche_reg_pct) / 2, 2)

        results.append({
            "domain": d["domain"],
            "city": d["city"],
            "niche": d["niche"],
            "status": d["status"],
            "city_registered_pct": city_reg_pct,
            "niche_registered_pct": niche_reg_pct,
            "total_score": total_score,
        })

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results
