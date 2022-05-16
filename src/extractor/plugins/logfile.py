"""Logfile Plugin to log Extraction-Events to a file"""

import logging
from extractor.common import Plugin

# logger = logging.getLogger(__name__)


class Logfile(Plugin):
    """Provides File logging functionality"""

    exclude = [
        "before_acquire_folders",
        "after_acquire_folders",
        "before_acquire_files",
        "after_acquire_files",
    ]

    def __init__(self, logfile):
        _logger = logging.getLogger("extractor_logfile")
        _logger.setLevel(logging.INFO)
        _logger.propagate = False
        _formatter = logging.Formatter("%(asctime)s - %(message)s")
        _fh = logging.FileHandler(logfile, mode="w")
        _fh.setLevel(logging.INFO)
        _fh.setFormatter(_formatter)
        _logger.addHandler(_fh)

        self._logger = _logger

    @property
    def logger(self):
        return self._logger

    def log(self, message: str):
        self.logger.info(message)

    def on(self, event, *args, **kwargs):
        if event not in self.exclude:
            self.log(event)

    def on_extractor_start(self):
        self.logger.info("EXTRACTION_START")

    def on_extractor_end(self):
        self.logger.info("EXTRACTION_FINISHED")

    def on_login_success(self, user):
        self.logger.info("LOGIN_SUCCESS %s", user)

    def on_login_failure(self, exception):
        self.logger.error("LOGIN_FAILED %s", exception)

    def on_folder_found(self, folder):
        self.logger.info("FOLDER_FOUND %s", folder)

    def on_file_found(self, file):
        self.logger.info("FILE_FOUND %s", file)
