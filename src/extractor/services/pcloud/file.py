"""pCloud File Class"""

from dataclasses import dataclass, field
from extractor.data import File
from extractor.errors import DownloadError
from extractor.common.tools import iterable_to_stream
from extractor.services.pcloud.client import Client


@dataclass
class PCloudFile(File):
    """pCloud File Class"""

    session: Client = field(compare=False, hash=False, repr=False)

    def get_stream(self):
        # open remote filehandle
        resp = self.session.file_open(fileid=self.id, flags=0)
        if resp.get("result") != 0:
            raise DownloadError(
                f"pCloud error occured ({resp['result']}) - {resp['error']}", self
            )

        file_descriptor = resp["fd"]
        response = self.session.file_read(
            fd=file_descriptor, count=self.size, stream=True
        )

        buffer_size = 4096
        stream = iterable_to_stream(
            response.iter_content(chunk_size=buffer_size), buffer_size=buffer_size
        )

        return stream

    def __enter__(self):
        return self.get_stream()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        ...
