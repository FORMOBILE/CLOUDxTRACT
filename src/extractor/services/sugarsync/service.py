from typing import List
import iso8601
from extractor.common import CloudService
from extractor.errors import NotLoggedInError
from extractor.data import User
from extractor.data import Folder
from extractor.data import File
from extractor.services.sugarsync.folder import SugarsyncFolder
from .client import Client


class SugarsyncService(CloudService):
    def __init__(self, app_id, app_access_key, app_private_key):
        self._app_id = app_id
        self._app_access_key = app_access_key
        self._app_private_key = app_private_key
        self.client = None

    def login(self, username: str, password: str) -> User:
        self.client = Client(
            app_id=self._app_id,
            app_access_key=self._app_access_key,
            app_private_key=self._app_private_key,
            username=username,
            password=password,
        )

        return self.user

    @property
    def is_logged_in(self) -> bool:
        return self.client is not None

    @property
    def user(self) -> User:
        if not self.is_logged_in:
            raise NotLoggedInError

        user = self.client.user

        return User(
            id=int(user.get("ref").split("/")[-1]),
            # given_name=None,
            # surname=None
            displayname=user.get("nickname"),
            email=user.get("username"),
            # phone=None,
        )

    @property
    def folders(self) -> List[Folder]:
        if not self.is_logged_in:
            raise NotLoggedInError

        def recursive(folder: SugarsyncFolder):
            yield folder
            for child_folder in folder.folders:
                yield from recursive(child_folder)

        for folder in self.client.get_syncfolders():

            created_at = folder.get("timeCreated")
            iso8601.parse_date(created_at)

            f = SugarsyncFolder(
                id=folder.get("dsid"),
                name=folder.get("displayName"),
                path=folder.get("displayName"),
                owner=True,
                shared=folder.get("sharing", {}).get("@enabled") == "true",
                created_at=created_at,
                modified_at=None,
                session=self.client,
            )

            yield from recursive(f)

    @property
    def files(self) -> List[File]:
        for folder in self.folders:
            yield from folder.files
