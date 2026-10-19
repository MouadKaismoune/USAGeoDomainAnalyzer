from moduls.cities.services import (
    delete_city, get_all_cities_with_stats, set_city_ignore
)
from translator import translator as t


def get_cities_table_data():
    return get_all_cities_with_stats()


def handle_delete_city(name: str):
    success, msg_key = delete_city(name)
    return success, t.t(f"cities_{msg_key}")


def handle_set_city_ignore(name: str, ignored: bool):
    set_city_ignore(name, ignored)
