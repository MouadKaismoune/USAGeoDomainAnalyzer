import random

from database import db
from database.models import NicheModel
from moduls.domains.rdap import classify_status

model = NicheModel(db)


def _parse_date(text):
    """Parse a stored ``dd-mm-yyyy`` date into a sortable ``(y, m, d)`` tuple."""
    if not text:
        return None
    try:
        day, month, year = text.strip().split("-")
        return (int(year), int(month), int(day))
    except (ValueError, TypeError):
        return None


def set_niche_ignore(name: str, value: bool):
    model.set_ignore(name, value)


def get_unchecked_niches():
    return model.get_unchecked()


def get_unchecked_niche_names():
    return model.get_unchecked_names()


def get_oldest_niche_names(count: int):
    """Return up to ``count`` niche names that are oldest by last check date.

    Only niches that were already checked are considered, ordered from the
    oldest ``checked_date``. Niches sharing the same date are picked at random,
    and never-checked niches fill any remaining slots. Ignored niches are
    skipped.
    """
    count = max(1, int(count))
    rows = db.fetch_all("SELECT name, checked_date FROM niches WHERE ignore_it = 0")
    if not rows:
        return []

    checked = []
    unchecked = []
    for row in rows:
        parsed = _parse_date(row["checked_date"])
        if parsed is None:
            unchecked.append(row["name"])
        else:
            checked.append((row["name"], parsed))

    # Shuffle first so that the stable sort below randomises niches that share
    # the same date while still ordering by date overall.
    random.shuffle(checked)
    checked.sort(key=lambda item: item[1])
    names = [name for name, _ in checked][:count]

    if len(names) < count:
        random.shuffle(unchecked)
        names.extend(unchecked[: count - len(names)])

    return names


def add_niche(name: str) -> tuple:
    if model.exists(name):
        return False, "already_exists"
    model.add(name)
    return True, "added_success"


def delete_niche(name: str) -> tuple:
    if not model.exists(name):
        return False, "not_found"
    from moduls.domains.services import delete_domains_by_niche
    with db.transaction() as conn:
        delete_domains_by_niche(name, conn=conn)
        model.delete(name, conn=conn)
    return True, "deleted_success"


def mark_checked(name: str, date: str = None, conn=None):
    model.set_checked(name, date, conn=conn)


def reset_niche(name: str) -> tuple:
    if not model.exists(name):
        return False, "not_found"
    from moduls.domains.services import delete_domains_by_niche
    with db.transaction() as conn:
        delete_domains_by_niche(name, conn=conn)
        model.reset_checked(name, conn=conn)
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
