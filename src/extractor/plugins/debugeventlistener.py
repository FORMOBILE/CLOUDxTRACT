import logging

from extractor.common import Plugin

logger = logging.getLogger(__name__)


class DebugEventListener(Plugin):
    """
    Log Events to the default Logger
    """

    def on(self, event, *args, **kwargs):
        logger.debug("Event [%s] raised", event)

    def on_login_success(self, user):
        logger.debug("Event [login_success] raised. %s", user)

    def on_login_failure(self, exception):
        logger.debug("Event [login_failure] raised. %s", exception)

    def on_folder_found(self, folder):
        logger.debug("Event [folder_found] raised. %s", folder)

    def on_file_found(self, file):
        logger.debug("Event [file_found] raised. %s", file)

    def on_file_download_success(self, file, destination):
        logger.debug("Event [file_download_success] raised. %s %s", file, destination)

    def on_file_download_failed(self, file, error):
        logger.debug("Event [file_download_failed] raised. %s %s", file, error)
