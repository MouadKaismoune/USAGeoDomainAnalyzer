from moduls.strength.services import calculate_domain_strength, get_domains_view


def get_strength_results():
    results = calculate_domain_strength()
    return results


__all__ = ["get_strength_results", "get_domains_view"]
