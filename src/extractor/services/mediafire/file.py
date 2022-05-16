# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Optional
from dataclasses import dataclass, field

import requests
from extractor.common.tools import iterable_to_stream
from extractor.data import File
from extractor.errors import DownloadError
from extractor.services.pcloud.client import Client


@dataclass
class MediafireFile(File):

    link: Optional[str] = field(compare=False, hash=False, repr=False)
    session: Client = field(compare=False, hash=False, repr=False)

    def get_stream(self):
        if not self.link:
            try:
                result = self.session.file_get_links(
                    quick_key=self.id, link_type="direct_download"
                )
                self.link = result["links"][0]["direct_download"].replace(
                    "http:", "https:"
                )
            except Exception as ex:
                raise DownloadError("No Downloadlink given") from ex

        response = requests.get(self.link, stream=True)
        buffer_size = 4096
        stream = iterable_to_stream(
            response.iter_content(chunk_size=buffer_size), buffer_size=buffer_size
        )

        return stream

    def __enter__(self):
        return self.get_stream()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        ...
