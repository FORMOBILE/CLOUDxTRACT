import logging
from pathlib import Path
from extractor import Extractor
from extractor.data import Folder
from extractor.data import File
from extractor.common import Plugin
from extractor.errors import DownloadError

logger = logging.getLogger(__name__)


class Downloader(Plugin):
    def __init__(self, path):
        self._extractor = None
        self._basepath = Path(path).absolute()

    def init(self, extractor: Extractor):
        self._extractor = extractor

    def on_folder_found(self, folder: Folder):
        """
        Eventhandler for Folder Found Event

        Create a Folder in the Filesystem with the Information provided by the Folder-Object
        """

        # Create Folder
        self._basepath.joinpath(folder.path).mkdir(exist_ok=True, parents=True)
        # TODO: Folder Attributes like Created/Modified Timestamps

    def on_file_found(self, file: File):
        """
        Eventhandler for File Found Event

        Acquire the File-Content and save them in the file system
        """
        try:
            # chunk_size = 4096
            # destination = self._basepath.joinpath(file.path)
            # source = self._extractor._service.file_get_stream(file)
            # with open(destination, "wb") as target:
            #     while True:
            #         chunk = source.read(chunk_size)
            #         target.write(chunk)
            #         if len(chunk) < chunk_size:
            #             break

            chunk_size = 4096
            destination = self._basepath.joinpath(file.path)
            with file as source, open(destination, "wb") as target:
                while True:
                    chunk = source.read(chunk_size)
                    target.write(chunk)
                    if len(chunk) < chunk_size:
                        break

        except Exception as error:
            self._extractor.emit("file_download_failed", file, str(error))
        else:
            self._extractor.emit("file_download_success", file, destination)
