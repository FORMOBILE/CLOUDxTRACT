import argparse
import logging
from argparse import RawTextHelpFormatter

from extractor import Extractor
from extractor.plugins import DebugEventListener, Downloader
from extractor.services.hidrive import HidriveService
from extractor.services.mediafire import MediafireService
from extractor.services.nextcloud import NextcloudService
from extractor.services.pcloud import PCloudService
from extractor.services.sugarsync import SugarsyncService

logging.getLogger("urllib3").setLevel(
    logging.CRITICAL)  # Disable urllib3 log entries
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger("extractor")
logger.setLevel(level=logging.DEBUG)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter("%(asctime)s | %(message)s")
fh.setFormatter(fh_formatter)
logger.addHandler(fh)


def main():
    # define input parameter
    parser = argparse.ArgumentParser(
        description="CloudXtractor\n\nThis project has received funding from the European Union's Horizon 2020 - Research and Innovation Framework Programme, H2020-SU-SEC-2018, under grant agreement no. 832800",
        usage="python -m extractor",
        formatter_class=RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        title="Supported Cloudservices",
        dest="service",
        required=True,
    )

    #
    # PCloud
    #
    parser_pcloud = subparsers.add_parser("pcloud", help="plcoud help")
    parser_pcloud.add_argument(
        "--confirm-legal",
        required=False,
        action="store_true",
        dest="legal",
        help="Confirmation that all legal requirements met",
    )
    parser_pcloud.add_argument(
        "--logfile",
        type=str,
        required=False,
        dest="logfile",
        help="Logfile",
    )
    parser_pcloud.add_argument(
        "-u",
        type=str,
        required=True,
        metavar="Username",
        dest="username",
        help="Username of the Account to examine",
    )
    parser_pcloud.add_argument(
        "-p",
        type=str,
        required=True,
        metavar="Password",
        dest="password",
        help="Password of the Account to examine",
    )
    parser_pcloud.add_argument(
        "path",
        type=str,
        nargs="?",
        metavar="Destination",
        help="Local Path to store files. If not provided, no download is carried out.",
        default=None,
    )

    #
    # MediaFire
    #
    parser_mediafire = subparsers.add_parser(
        "mediafire", help="mediafire help")
    parser_mediafire.add_argument(
        "--confirm-legal",
        required=False,
        action="store_true",
        dest="legal",
        help="Confirmation that all legal requirements met",
    )
    parser_mediafire.add_argument(
        "--logfile",
        type=str,
        required=False,
        dest="logfile",
        help="Logfile",
    )
    parser_mediafire.add_argument(
        "-u",
        type=str,
        required=True,
        metavar="Username",
        dest="username",
        help="Username of the Account to examine",
    )
    parser_mediafire.add_argument(
        "-p",
        type=str,
        required=True,
        metavar="Password",
        dest="password",
        help="Password of the Account to examine",
    )
    parser_mediafire.add_argument(
        "path",
        type=str,
        nargs="?",
        metavar="Destination",
        help="Local Path to store files. If not provided, no download is carried out.",
        default=None,
    )

    #
    # SugarSync
    #
    parser_sugarsync = subparsers.add_parser(
        "sugarsync", help="sugarsync help")
    parser_sugarsync.add_argument(
        "--confirm-legal",
        required=False,
        action="store_true",
        dest="legal",
        help="Confirmation that all legal requirements met",
    )
    parser_sugarsync.add_argument(
        "--logfile",
        type=str,
        required=False,
        dest="logfile",
        help="Logfile",
    )
    parser_sugarsync.add_argument(
        "-app_id",
        type=str,
        required=True,
        metavar="AppID",
        dest="app_id",
        help="Application ID",
    )
    parser_sugarsync.add_argument(
        "-app_access_key",
        type=str,
        required=True,
        metavar="AccessKey",
        dest="app_access_key",
        help="Application Access Key",
    )
    parser_sugarsync.add_argument(
        "-app_private_key",
        type=str,
        required=True,
        metavar="PrivateKey",
        dest="app_private_key",
        help="Application Private Key",
    )
    parser_sugarsync.add_argument(
        "-u",
        type=str,
        required=True,
        metavar="Username",
        dest="username",
        help="Username of the Account to examine",
    )
    parser_sugarsync.add_argument(
        "-p",
        type=str,
        required=True,
        metavar="Password",
        dest="password",
        help="Password of the Account to examine",
    )
    parser_sugarsync.add_argument(
        "path",
        type=str,
        nargs="?",
        metavar="Destination",
        help="Local Path to store files. If not provided, no download is carried out.",
        default=None,
    )

    #
    # Highdrive
    #
    parser_hidrive = subparsers.add_parser("highdrive", help="highdrive help")
    parser_hidrive.add_argument(
        "--confirm-legal",
        required=False,
        action="store_true",
        dest="legal",
        help="Confirmation that all legal requirements met",
    )
    parser_hidrive.add_argument(
        "--logfile",
        type=str,
        required=False,
        dest="logfile",
        help="Logfile",
    )
    parser_hidrive.add_argument(
        "-u",
        type=str,
        required=True,
        metavar="Username",
        dest="username",
        help="Username of the Account to examine",
    )
    parser_hidrive.add_argument(
        "-p",
        type=str,
        required=True,
        metavar="Password",
        dest="password",
        help="Password of the Account to examine",
    )
    parser_hidrive.add_argument(
        "path",
        type=str,
        nargs="?",
        metavar="Destination",
        help="Local Path to store files. If not provided, no download is carried out.",
        default=None,
    )

    #
    # Nextcloud
    #
    parser_nextcloud = subparsers.add_parser(
        "nextcloud", help="nextcloud help")
    parser_nextcloud.add_argument(
        "--confirm-legal",
        required=False,
        action="store_true",
        dest="legal",
        help="Confirmation that all legal requirements met",
    )
    parser_nextcloud.add_argument(
        "--logfile",
        type=str,
        required=False,
        dest="logfile",
        help="Logfile",
    )
    parser_nextcloud.add_argument(
        "-url",
        type=str,
        required=True,
        metavar="Host URL",
        dest="url",
        help="The URL of the Nextcloud server",
    )
    parser_nextcloud.add_argument(
        "-u",
        type=str,
        required=True,
        metavar="Username",
        dest="username",
        help="Username of the Account to examine",
    )
    parser_nextcloud.add_argument(
        "-p",
        type=str,
        required=True,
        metavar="Password",
        dest="password",
        help="Password of the Account to examine",
    )
    parser_nextcloud.add_argument(
        "path",
        type=str,
        nargs="?",
        metavar="Destination",
        help="Local Path to store files. If not provided, no download is carried out.",
        default=None,
    )

    args = parser.parse_args()
    username = args.username
    password = args.password

    if args.service == "pcloud":
        service = PCloudService()
    elif args.service == "mediafire":
        service = MediafireService()
    elif args.service == "sugarsync":
        service = SugarsyncService(
            app_id=args.app_id,
            app_access_key=args.app_access_key,
            app_private_key=args.app_private_key,
        )
    elif args.service == "highdrive":
        service = HidriveService()
    elif args.service == "nextcloud":
        service = NextcloudService(url=args.url)
    else:
        service = None

    plugins = [DebugEventListener()]

    if args.path is not None:
        plugins.append(Downloader(args.path))

    extractor = Extractor(service, plugins)
    extractor.acquire(username, password)


if __name__ == "__main__":
    main()
