from moduls.domains.services import get_all_domains_with_strength


def get_domains_table_data(status_filter="All"):
    domains = get_all_domains_with_strength()
    if status_filter and status_filter != "All":
        key = status_filter.lower()
        domains = [d for d in domains if key in d["status"].lower()]
    return domains
