"""
[summary]
"""
import logging
from functools import lru_cache
from typing import List
from extractor.common import CloudService
from extractor.data import User
from extractor.data.folder import Folder
from extractor.errors import NotLoggedInError
from .file import MediafireFile as File
from .folder import MediafireFolder
from .client import Client


logger = logging.getLogger(__name__)


class MediafireService(CloudService):
    """
    Serviceclass for Mediafire
    """

    def __init__(self):
        self.client = None

    def login(self, username: str, password: str) -> User:
        self.client = Client(email=username, password=password)
        return self.user

    @property
    def is_logged_in(self) -> bool:
        """
        Returns if the user is logged in

        Returns:
            bool: if the user is logged in correctly
        """
        return self.client is not None

    @property
    @lru_cache(maxsize=1)
    def user(self) -> User:
        if not self.is_logged_in:
            raise NotLoggedInError

        try:
            data = self.client.user_get_info()
        except Exception:
            raise
        else:
            return User(
                id=data["user_info"]["ekey"],
                email=data["user_info"]["email"],
                given_name=data["user_info"]["first_name"],
                surname=data["user_info"]["last_name"],
                displayname=data["user_info"]["display_name"],
            )

    @lru_cache(maxsize=1)
    def get_root(self):
        if not self.is_logged_in:
            raise NotLoggedInError

        data = self.client.folder_get_info(folder_key=None)
        if not data["result"] == "Success":
            # TODO ErrorHandling
            pass

        data = data["folder_info"]

        folder = MediafireFolder(
            session=self.client,
            id=data["folderkey"],
            path="",
            name=data["name"],
            owner=True,
            shared=False,
            created_at=None,
            modified_at=None,
        )

        return folder

    @property
    def folders(self) -> List[Folder]:
        if not self.is_logged_in:
            raise NotLoggedInError

        def recursive(folder):
            for subfolder in folder.folders:
                yield subfolder
                yield from recursive(subfolder)

        root = self.get_root()
        yield from recursive(root)

    @property
    def files(self) -> List[File]:
        """
        Return Files
        """

        def recursive(directory):
            for file in directory.files:
                yield file

            for subdir in directory.folders:
                yield from recursive(subdir)

        if not self.is_logged_in:
            raise NotLoggedInError

        root = self.get_root()
        yield from recursive(root)

    def file_get_stream(self, file: File):
        return file.get_stream()
