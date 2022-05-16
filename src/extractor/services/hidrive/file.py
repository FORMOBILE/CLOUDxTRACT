from io import BufferedReader
from dataclasses import dataclass, field
from extractor.common.tools import iterable_to_stream
from extractor.data import File
from extractor.services.hidrive.client import Client


@dataclass
class HidriveFile(File):
    session: Client = field(compare=False, hash=False, repr=False)

    def get_stream(self) -> BufferedReader:
        response = self.session.get_file_content_stream(f"/{self.path}")

        buffer_size = 4096
        return iterable_to_stream(
            response.iter_content(chunk_size=buffer_size), buffer_size=buffer_size
        )

    def __enter__(self):
        return self.get_stream()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        ...
