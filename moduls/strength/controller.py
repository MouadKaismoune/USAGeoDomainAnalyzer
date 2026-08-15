from moduls.strength.services import calculate_domain_strength
from translator import translator as t


def get_strength_results():
    results = calculate_domain_strength()
    return results
