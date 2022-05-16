import logging
import sys

import PySimpleGUI as sg

from extractor import Extractor
from extractor.plugins.xrylogfile import XRYLogfile
from extractor.services.nextcloud import NextcloudService

__contact__ = "martin.bochmann@hs-mittweida.de"
__version__ = "0.1"
__description__ = "CloudXtract-XRY-Testscript-Nextcloud"
__date__ = "15 March 2021"

logging.getLogger("urllib3").setLevel(
    logging.CRITICAL)  # Disable urllib3 log entries
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main(image, _):

    # Credential Window
    event, values = sg.Window(
        "Please insert the credentials",
        [
            [sg.Text("Nextcloud URL"), sg.InputText(key="-URL-")],
            [sg.Text("Username"), sg.InputText(key="-USERNAME-")],
            [sg.Text("Password"), sg.InputText(
                key="-PASSWORD-", password_char="*")],
            [sg.Submit(), sg.Cancel()],
        ],
    ).read(close=True)

    if event in (sg.WIN_CLOSED, "Cancel"):  # if user closes window or clicks cancel
        logging.warning("User cancelled the credential input!")
        sys.exit(87)

    url = values["-URL-"]
    username = values["-USERNAME-"]
    password = values["-PASSWORD-"]

    service = NextcloudService(
        url=url
    )
    plugins = [XRYLogfile(image)]

    extractor = Extractor(service, plugins)
    extractor.acquire(username, password)
