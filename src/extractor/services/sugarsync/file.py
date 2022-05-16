from io import BufferedReader
from dataclasses import dataclass, field
from extractor.common.tools import iterable_to_stream
from extractor.data import File
from extractor.services.sugarsync.client import Client


@dataclass
class SugarsyncFile(File):
    session: Client = field(compare=False, hash=False, repr=False)

    def get_stream(self) -> BufferedReader:
        url = f"https://api.sugarsync.com/file/{self.id.replace('/',':')}/data"
        response = self.session.get_file_content_stream_by_url(url)
        buffer_size = 4096

        stream = iterable_to_stream(
            response.iter_content(chunk_size=buffer_size), buffer_size=buffer_size
        )

        return stream

    def __enter__(self):
        return self.get_stream()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        ...
