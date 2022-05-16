from typing import Iterator
from dataclasses import dataclass, field
import iso8601
from extractor.data import Folder, File
from extractor.services.sugarsync.client import Client
from extractor.services.sugarsync.file import SugarsyncFile


@dataclass
class SugarsyncFolder(Folder):
    session: Client = field(compare=False, hash=False, repr=False)

    @property
    def folders(self) -> Iterator[Folder]:
        url = f"https://api.sugarsync.com/folder/{self.id.replace('/',':')}/contents?type=folder"

        for data in self.session.get_folder_contents_by_url(url):

            created_at = data.get("timeCreated")
            iso8601.parse_date(created_at)

            folder = SugarsyncFolder(
                id=data.get("dsid"),
                name=data.get("displayName"),
                path=self.path + "/" + data.get("displayName"),
                owner=True,
                shared=data.get("sharing", {}).get("@enabled") == "true",
                created_at=created_at,
                modified_at=None,
                session=self.session,
            )

            yield folder

    @property
    def files(self) -> Iterator[File]:
        url = f"https://api.sugarsync.com/folder/{self.id.replace('/',':')}/contents?type=file"

        for data in self.session.get_folder_contents_by_url(url):

            created_at = data.get("timeCreated")
            iso8601.parse_date(created_at)

            yield SugarsyncFile(
                id=data.get("dsid"),
                name=data.get("displayName"),
                path=self.path + "/" + data.get("displayName"),
                size=int(data.get("size")),
                owner=True,
                shared=data.get("sharing", {}).get("@enabled") == "true",
                created_at=created_at,
                modified_at=None,
                session=self.session,
            )
