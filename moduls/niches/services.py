from database import db
from database.models import NicheModel

model = NicheModel(db)


def get_all_niches():
    return model.get_all()


def get_niche_names():
    return model.get_names()


def set_niche_ignore(name: str, value: bool):
    model.set_ignore(name, value)


def get_ignored_niche_names():
    rows = db.fetch_all("SELECT name FROM niches WHERE ignore_it = 1")
    return {r["name"] for r in rows}


def get_unchecked_niches():
    return model.get_unchecked()


def get_unchecked_niche_names():
    return model.get_unchecked_names()


def add_niche(name: str) -> tuple:
    if model.exists(name):
        return False, "already_exists"
    model.add(name)
    return True, "added_success"


def delete_niche(name: str) -> tuple:
    if not model.exists(name):
        return False, "not_found"
    from moduls.domains.services import delete_domains_by_niche
    from database.models import NicheSummaryModel
    delete_domains_by_niche(name)
    summary_model = NicheSummaryModel(db)
    summary_model.delete_by_niche(name)
    model.delete(name)
    return True, "deleted_success"


def mark_checked(name: str, date: str = None):
    model.set_checked(name, date)


def mark_unchecked(name: str):
    model.reset_checked(name)


def reset_niche(name: str) -> tuple:
    if not model.exists(name):
        return False, "not_found"
    from moduls.domains.services import delete_domains_by_niche
    from database.models import NicheSummaryModel
    delete_domains_by_niche(name)
    summary_model = NicheSummaryModel(db)
    summary_model.delete_by_niche(name)
    model.reset_checked(name)
    return True, "reset_success"


def get_niche_count():
    return model.count()


def get_checked_count():
    return model.count_checked()


def get_unchecked_count():
    return model.count_unchecked()


def get_niche_stats(niche_name: str):
    rows = db.fetch_all(
        "SELECT status, COUNT(*) as cnt FROM domains WHERE niche = ? GROUP BY status",
        (niche_name,),
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


def get_all_niches_with_stats():
    niches = model.get_all()
    result = []
    for niche in niches:
        stats = get_niche_stats(niche["name"])
        result.append({
            "id": niche["id"],
            "name": niche["name"],
            "ignore_it": niche["ignore_it"],
            "is_checked": niche["is_checked"],
            "checked_date": niche.get("checked_date", ""),
            "available": stats["available"],
            "registered": stats["registered"],
            "unknown": stats["unknown"],
            "total": stats["total"],
            "strength": stats["registered_pct"],
        })
    return result
