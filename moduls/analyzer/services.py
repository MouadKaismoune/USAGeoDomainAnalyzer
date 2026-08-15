import time
import requests
from datetime import datetime
from moduls.cities.services import get_city_names
from moduls.niches.services import get_unchecked_niche_names, mark_checked
from moduls.domains.services import add_domains_bulk
from database import db
from database.models import NicheSummaryModel

summary_model = NicheSummaryModel(db)

RUNNING = False


def stop_analysis():
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
            if "available" in status_lower and "registered" not in status_lower:
                niche_available += 1
            elif "registered" in status_lower:
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

            time.sleep(delay_between_cities)

        if not RUNNING:
            break

        if records:
            add_domains_bulk(records)
            summary_model.upsert(niche, niche_available, niche_registered, niche_unknown, date_today)
            mark_checked(niche, date_today)

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
            remaining = delay_between_niches
            while remaining > 0 and RUNNING:
                time.sleep(1)
                remaining -= 1

    RUNNING = False
    return True, "completed"
