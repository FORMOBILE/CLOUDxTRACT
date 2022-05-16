import sys
import logging
import PySimpleGUI as sg
from extractor import Extractor
from extractor.services.hidrive import HidriveService
from extractor.plugins.xrylogfile import XRYLogfile

__contact__ = "martin.bochmann@hs-mittweida.de"
__version__ = "0.1"
__description__ = "CloudXtract-XRY-Testscript-StratoHidrive"
__date__ = "20 February 2022"

logging.getLogger("urllib3").setLevel(logging.CRITICAL)  # Disable urllib3 log entries
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main(image, _):

    # Credential Window
    event, values = sg.Window(
        "Please insert the credentials",
        [
            [sg.Text("Username"), sg.InputText(key="-USERNAME-")],
            [sg.Text("Password"), sg.InputText(key="-PASSWORD-", password_char="*")],
            [sg.Submit(), sg.Cancel()],
        ],
    ).read(close=True)

    if event in (sg.WIN_CLOSED, "Cancel"):  # if user closes window or clicks cancel
        logging.warning("User cancelled the credential input!")
        sys.exit(87)

    username = values["-USERNAME-"]
    password = values["-PASSWORD-"]

    service = HidriveService()
    plugins = [XRYLogfile(image)]

    extractor = Extractor(service, plugins)
    extractor.acquire(username, password)
