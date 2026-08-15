from moduls.niches.services import (
    get_all_niches, add_niche, delete_niche, reset_niche, get_niche_names,
    get_unchecked_niches, get_all_niches_with_stats, set_niche_ignore
)
from translator import translator as t


def get_niches_table_data():
    return get_all_niches_with_stats()


def get_niches_names_list():
    return get_niche_names()


def get_unchecked_niches_data():
    return get_unchecked_niches()


def handle_add_niche(name: str):
    success, msg_key = add_niche(name)
    return success, t.t(f"niches_{msg_key}")


def handle_delete_niche(name: str):
    success, msg_key = delete_niche(name)
    return success, t.t(f"niches_{msg_key}")


def handle_reset_niche(name: str):
    success, msg_key = reset_niche(name)
    return success, t.t(f"niches_{msg_key}")


def handle_set_niche_ignore(name: str, ignored: bool):
    set_niche_ignore(name, ignored)
