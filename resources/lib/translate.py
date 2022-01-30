from resources.lib.addonutils import LANGUAGE
from resources.lib.addonutils import log

T_MAP = {
    'menu.anime': 33001,
    'menu.movies': 33002,
    'menu.shows': 33003,
    'menu.series': 33004,
    'input.email': 40001,
    'input.password': 40002,
    'no.credentials': 40003,
    'login.error': 40004,
}


def translatedString(id):
    t_string = T_MAP.get(id)
    if t_string:
        return LANGUAGE(t_string)
    log(f"{id} translation ID not found.", 3)
    return 'NO TRANSLATION AVAILABLE'
