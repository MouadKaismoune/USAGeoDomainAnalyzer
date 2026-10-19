from moduls.domains.rdap import is_available
from moduls.domains.services import get_all_domains_with_strength


def _rank_available(rows):
    """Keep only available domains and rank them by strength score."""
    results = []
    for d in rows:
        if not is_available(d["status"]):
            continue
        results.append({
            "domain": d["domain"],
            "city": d["city"],
            "niche": d["niche"],
            "status": d["status"],
            "city_registered_pct": d["city_strength"],
            "niche_registered_pct": d["niche_strength"],
            "total_score": d["strength"],
        })
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results


def calculate_domain_strength():
    """Rank available domains by strength.

    Reuses ``get_all_domains_with_strength`` (the single strength computation)
    and keeps only the available rows, so both views can never disagree.
    """
    return _rank_available(get_all_domains_with_strength())


def get_domains_view():
    """Return ``(all_rows, available_ranked)`` from one strength computation.

    The Domains page shows the full table and the available-only strength tab.
    Computing the dataset once here avoids running
    ``get_all_domains_with_strength`` twice per refresh.
    """
    rows = get_all_domains_with_strength()
    return rows, _rank_available(rows)
