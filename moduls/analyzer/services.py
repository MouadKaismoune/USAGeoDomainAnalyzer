import time
from datetime import datetime
from moduls.cities.services import get_city_names
from moduls.niches.services import (
    get_unchecked_niche_names, mark_checked, reset_niche,
)
from moduls.domains.services import add_domains_bulk
from moduls.domains.rdap import (
    AVAILABLE, REGISTERED, check_domain_rdap, classify_status,
)
from database import db

RUNNING = False


def stop_analysis():
    global RUNNING
    RUNNING = False


def _interruptible_sleep(seconds):
    """Sleep in short steps so ``stop_analysis()`` takes effect quickly."""
    remaining = float(seconds)
    while remaining > 0 and RUNNING:
        time.sleep(min(0.25, remaining))
        remaining -= 0.25


def _reset_if_checked(niche, progress_callback):
    """Drop a previously checked niche's results before re-checking it.

    Re-running the analysis on an already-checked niche would otherwise append
    duplicate domains. Returns ``True`` when a reset happened so the caller can
    log it.
    """
    row = db.fetch_one("SELECT is_checked FROM niches WHERE name = ?", (niche,))
    if not row or not row["is_checked"]:
        return False

    reset_niche(niche)
    if progress_callback:
        progress_callback(type="niche_reset", niche=niche)
    return True


def run_analysis(selected_niches=None, delay_between_cities=2, delay_between_niches=30, progress_callback=None):
    global RUNNING
    RUNNING = True

    cities = get_city_names()
    if not cities:
        return False, "analyzer_no_cities"

    if selected_niches:
        niches = selected_niches
    else:
        niches = get_unchecked_niche_names()

    if not niches:
        return False, "analyzer_no_niches"

    date_today = datetime.today().strftime("%d-%m-%Y")
    total_niches = len(niches)
    total_cities = len(cities)

    for niche_idx, niche in enumerate(niches):
        if not RUNNING:
            break

        # Re-checking an already checked niche: clear its old results first so
        # duplicates are never added.
        if _reset_if_checked(niche, progress_callback) and not RUNNING:
            break

        niche_available = 0
        niche_registered = 0
        niche_unknown = 0

        if progress_callback:
            progress_callback(
                type="niche_start",
                niche=niche,
                niche_index=niche_idx + 1,
                total_niches=total_niches,
            )

        records = []
        for city_idx, city in enumerate(cities):
            if not RUNNING:
                break

            domain = f"{city}{niche}.com"
            status = check_domain_rdap(domain)
            records.append((domain, status, city, niche, date_today))

            status_lower = status.lower()
            bucket = classify_status(status_lower)
            if bucket == AVAILABLE:
                niche_available += 1
            elif bucket == REGISTERED:
                niche_registered += 1
            else:
                niche_unknown += 1

            if progress_callback:
                progress_callback(
                    type="domain_check",
                    domain=domain,
                    status=status,
                    city=city,
                    city_index=city_idx + 1,
                    total_cities=total_cities,
                    niche=niche,
                    niche_index=niche_idx + 1,
                    total_niches=total_niches,
                )

            _interruptible_sleep(delay_between_cities)

        if not RUNNING:
            break

        if records:
            # Domains and the "checked" flag are committed together so a niche
            # is never left with saved domains but still marked unchecked.
            with db.transaction() as conn:
                add_domains_bulk(records, conn=conn)
                mark_checked(niche, date_today, conn=conn)

        if progress_callback:
            progress_callback(
                type="niche_done",
                niche=niche,
                niche_index=niche_idx + 1,
                total_niches=total_niches,
                available=niche_available,
                registered=niche_registered,
                unknown=niche_unknown,
            )

        if niche_idx < total_niches - 1 and RUNNING:
            if progress_callback:
                progress_callback(
                    type="delay",
                    seconds=delay_between_niches,
                    next_niche=niches[niche_idx + 1] if niche_idx + 1 < len(niches) else "",
                )
            _interruptible_sleep(delay_between_niches)

    RUNNING = False
    return True, "completed"
