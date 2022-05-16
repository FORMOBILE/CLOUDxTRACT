import logging
import sys

import PySimpleGUI as sg

from extractor import Extractor
from extractor.plugins.xrylogfile import XRYLogfile
from extractor.services.sugarsync import SugarsyncService

__contact__ = "martin.bochmann@hs-mittweida.de"
__version__ = "0.1"
__description__ = "CloudXtract-XRY-Testscript-Sugarsync"
__date__ = "15 March 2022"

logging.getLogger("urllib3").setLevel(
    logging.CRITICAL)  # Disable urllib3 log entries
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main(image, _):

    # Credential Window
    event, values = sg.Window(
        "Please insert the credentials",
        [
            [sg.Text("Sugarsync AppID"), sg.InputText(key="-APPID-")],
            [sg.Text("Sugarsync AppAccessKey"),
             sg.InputText(key="-APPACCESSKEY-")],
            [sg.Text("Sugarsync AppPrivateKey"),
             sg.InputText(key="-APPPRIVATEKEY-")],
            [sg.Text("Username"), sg.InputText(key="-USERNAME-")],
            [sg.Text("Password"), sg.InputText(
                key="-PASSWORD-", password_char="*")],
            [sg.Submit(), sg.Cancel()],
        ],
    ).read(close=True)

    if event in (sg.WIN_CLOSED, "Cancel"):  # if user closes window or clicks cancel
        logging.warning("User cancelled the credential input!")
        sys.exit(87)

    app_id = values["-APPID-"]
    app_access_key = values["-APPACCESSKEY-"]
    app_private_key = values["-APPPRIVATEKEY-"]
    username = values["-USERNAME-"]
    password = values["-PASSWORD-"]

    service = SugarsyncService(
        app_id=app_id, app_access_key=app_access_key, app_private_key=app_private_key
    )
    plugins = [XRYLogfile(image)]

    extractor = Extractor(service, plugins)
    extractor.acquire(username, password)
