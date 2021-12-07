import sys
from resources.lib.vvvvid import *
from resources.lib.main import runPlugin
from resources.lib import addonutils
import xbmcgui


def set_credentials_dialog():
    username = xbmcgui.Dialog().input("Inserire email:")
    password = xbmcgui.Dialog().input(
        "Inserire password:", option=xbmcgui.ALPHANUM_HIDE_INPUT
    )

    if not username or not password:
        return None

    addonutils.setSetting(id="username", value=username)
    addonutils.setSetting(id="password", value=password)

    return {"username": username, "password": password}


def get_credentials():
    username = addonutils.getSetting("username")
    if not username:
        return None

    password = addonutils.getSetting("password")
    if not password:
        return None

    return {"username": username, "password": password}


if __name__ == "__main__":
    import web_pdb
    credentials = get_credentials()
    if not credentials:
        xbmcgui.Dialog().ok(
            "VVVVID.it", "Configurare il plugin inserendo email e password"
        )
        credentials = set_credentials_dialog()

    if not credentials:
        xbmcgui.Dialog().ok("VVVVID.it", "ERRORE: email e/o password non validi")
        sys.exit(0)

    manageLogin(credentials)

    addonutils.setContent("files")
    runPlugin()
