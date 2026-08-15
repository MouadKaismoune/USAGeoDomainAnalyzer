from moduls.domains.services import get_all_domains, get_status_counts, get_domains_by_niche, get_domains_by_city, get_all_domains_with_strength
from moduls.cities.services import get_city_names
from moduls.niches.services import get_niche_names
from translator import translator as t


def get_domains_table_data(status_filter="All"):
    domains = get_all_domains_with_strength()
    if status_filter and status_filter != "All":
        key = status_filter.lower()
        domains = [d for d in domains if key in d["status"].lower()]
    return domains


def get_overview_stats():
    return get_status_counts()


def get_filter_options():
    return {
        "niches": get_niche_names(),
        "cities": get_city_names(),
    }
