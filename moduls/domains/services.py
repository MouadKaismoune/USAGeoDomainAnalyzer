from database import db
from database.models import DomainModel
from moduls.domains.rdap import classify_status

model = DomainModel(db)


# A domain counts as registered when its status contains "registered"; this is
# the exact rule of ``moduls.domains.rdap.is_registered`` (which checks the
# ``registered`` substring first), pushed into SQL to avoid a Python pass.
_REGISTERED_CASE = "LOWER(status) LIKE '%registered%'"

# Ignored cities/niches (``ignore_it = 1``) are filtered in SQL. Cities are
# compared case-insensitively, niches case-sensitively, matching the previous
# Python-side behaviour.
_ACTIVE_WHERE = (
    "LOWER(city) NOT IN (SELECT LOWER(name) FROM cities WHERE ignore_it = 1) "
    "AND niche NOT IN (SELECT name FROM niches WHERE ignore_it = 1)"
)


def get_status_counts():
    counts = model.count_by_status()
    result = {"available": 0, "registered": 0, "unknown": 0}
    for row in counts:
        result[classify_status(row["status"])] += row["cnt"]
    return result


def add_domains_bulk(records: list, conn=None):
    model.add_many(records, conn=conn)


def delete_domains_by_niche(niche: str, conn=None):
    return model.delete_by_niche(niche, conn=conn)


def _group_percentages(conn, group_expr):
    """Return ``{key: registered_pct}`` for one grouping, computed in SQL.

    ``group_expr`` is the SQL expression/column to group by; the returned keys
    match how the caller looks them up (lower-cased city, raw niche).
    """
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT {group_expr} AS k,
               COUNT(*) AS total,
               SUM(CASE WHEN {_REGISTERED_CASE} THEN 1 ELSE 0 END) AS reg
        FROM domains
        WHERE {_ACTIVE_WHERE}
        GROUP BY {group_expr}
        """
    )
    result = {}
    for row in cursor.fetchall():
        total = row["total"]
        if total:
            result[row["k"]] = round(row["reg"] / total * 100, 2)
    return result


def get_all_domains_with_strength():
    """Return active domains with their city/niche registered percentages.

    Grouping, counting and ignored-entity filtering run in SQLite; only the
    final per-row assembly stays in Python. All three statements share a single
    connection to avoid opening one per query.
    """
    conn = db.connect()
    try:
        city_pcts = _group_percentages(conn, "LOWER(city)")
        niche_pcts = _group_percentages(conn, "niche")

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT id, domain, status, city, niche, date
            FROM domains
            WHERE {_ACTIVE_WHERE}
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    result = []
    for d in rows:
        city_pct = city_pcts.get(d["city"].lower(), 0)
        niche_pct = niche_pcts.get(d["niche"], 0)
        result.append({
            "id": d["id"],
            "domain": d["domain"],
            "status": d["status"],
            "city": d["city"],
            "niche": d["niche"],
            "date": d["date"],
            "city_strength": city_pct,
            "niche_strength": niche_pct,
            "strength": round((city_pct + niche_pct) / 2, 2),
        })

    return result
