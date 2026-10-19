from moduls.maintenance.services import get_unknown_domains


def get_unknown_domains_table():
    domains = get_unknown_domains()
    result = []
    for d in domains:
        result.append({
            "id": d["id"],
            "domain": d["domain"],
            "status": d["status"],
            "city": d["city"],
            "niche": d["niche"],
            "date": d["date"],
        })
    return result


def get_maintenance_stats():
    domains = get_unknown_domains()
    count = len(domains)
    cities = set()
    niches = set()
    for d in domains:
        cities.add(d["city"])
        niches.add(d["niche"])
    return {
        "count": count,
        "cities": len(cities),
        "niches": len(niches),
    }
