import pytz
from typing import Iterable
from extractor.common import CloudService
from extractor.errors import NotLoggedInError
from extractor.data import User
from extractor.data import Folder
from extractor.data import File
from extractor.services.hidrive.client import Client
from extractor.services.hidrive.file import HidriveFile
from datetime import datetime


class HidriveService(CloudService):
    def __init__(self):
        self.client = None

    def login(self, username: str, password: str) -> User:
        try:
            client = Client(username=username, password=password)
        except Exception as ex:
            raise NotLoggedInError from ex
        else:
            self.client = client

        return self.user

    @property
    def is_logged_in(self) -> bool:
        return self.client is not None

    @property
    def user(self) -> User:
        if not self.is_logged_in:
            raise NotLoggedInError

        user_data = self.client.get_user_data()

        return User(
            id=user_data.get("account"),
            username=user_data.get("alias"),
            # given_name=None,
            # surname=None
            displayname=user_data.get("descr"),
            email=user_data.get("email"),
            # phone=None,
        )

    @property
    def folders(self) -> Iterable[Folder]:
        if not self.is_logged_in:
            raise NotLoggedInError

        def traverse(folder):
            if not folder.get("path") == "/":
                yield Folder(
                    id=folder.get("id"),
                    name=folder.get("name"),
                    path=folder.get("path")[1:],
                    owner=True,
                    shared=False,
                    created_at=datetime.fromtimestamp(folder.get("ctime"), tz=pytz.UTC)
                    if folder.get("ctime") is not None
                    else None,
                    modified_at=datetime.fromtimestamp(folder.get("mtime"), tz=pytz.UTC)
                    if folder.get("mtime") is not None
                    else None,
                )

            for subfolder in [
                item for item in folder.get("members", []) if item.get("type") == "dir"
            ]:
                try:
                    subfolder = self.client.get_directory(path=subfolder.get("path"))
                except Exception as ex:
                    pass
                else:
                    yield from traverse(subfolder)

        root = self.client.get_directory(path="/")
        yield from traverse(root)

    @property
    def files(self) -> Iterable[File]:
        if not self.is_logged_in:
            raise NotLoggedInError

        def traverse(folder):
            for file in [
                item for item in folder.get("members") if item.get("type") == "file"
            ]:
                yield HidriveFile(
                    id=file.get("id"),
                    name=file.get("name"),
                    path=file.get("path")[1:],
                    size=file.get("size"),
                    owner=True,
                    shared=False,
                    created_at=datetime.fromtimestamp(file.get("ctime"), tz=pytz.UTC)
                    if file.get("ctime") is not None
                    else None,
                    modified_at=datetime.fromtimestamp(file.get("mtime"), tz=pytz.UTC)
                    if file.get("mtime") is not None
                    else None,
                    session=self.client,
                )

            for subfolder in [
                item for item in folder.get("members", []) if item.get("type") == "dir"
            ]:
                try:
                    subfolder = self.client.get_directory(path=subfolder.get("path"))
                except Exception:
                    pass
                else:
                    yield from traverse(subfolder)

        root = self.client.get_directory(path="/")
        yield from traverse(root)
