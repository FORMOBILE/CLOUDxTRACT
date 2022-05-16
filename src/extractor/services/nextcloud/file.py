from dataclasses import dataclass, field
from io import BufferedReader, BytesIO

from extractor.common.tools import iterable_to_stream
from extractor.data import File

from nextcloud.api_wrappers.webdav import File as WebdavFile


@dataclass
class NextcloudFile(File):
    file: WebdavFile = field(compare=False, hash=False, repr=False)

    def get_stream(self) -> BufferedReader:
        content = self.file.fetch_file_content()

        buffer_size = 4096
        return iterable_to_stream(
            BytesIO(content), buffer_size=buffer_size
        )

    def __enter__(self):
        return self.get_stream()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        ...
