from typing import Iterable
from xml.sax.handler import all_properties

from extractor.common import CloudService
from extractor.data import File, Folder, User
from extractor.errors import NotLoggedInError
from extractor.services.nextcloud.file import NextcloudFile

from nextcloud import NextCloud


class NextcloudService(CloudService):
    def __init__(self, url=None):
        self.url = url
        self.client = None

    def login(self, username: str, password: str) -> User:
        try:
            client = NextCloud(
                endpoint=self.url, user=username, password=password, json_data=True)
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

        user_response = self.client.get_user()
        if not user_response.is_ok:
            pass

        user_data = user_response.data

        return User(
            id=user_data.get("id"),
            username=user_data.get("id"),
            # given_name=None,
            # surname=None
            displayname=user_data.get("displayname"),
            email=user_data.get("email"),
            phone=user_data.get("phone"),
        )

    @property
    def folders(self) -> Iterable[Folder]:
        if not self.is_logged_in:
            raise NotLoggedInError

        user_id = self.user.id  # Cache user_id
        root = self.client.get_folder(all_properties=True)

        def _list_rec(item):
            if item.isdir() and not item.basename() == "":
                yield Folder(id=item.file_id, name=item.basename(), path=item.get_relative_path()[1:-1], owner=item.owner_id == user_id, shared=None, created_at=None, modified_at=item.last_modified_datetime)

            for i in [i for i in item.list(all_properties=True) if i.isdir()]:
                yield from _list_rec(i)

        yield from _list_rec(root)

    @property
    def files(self) -> Iterable[File]:
        if not self.is_logged_in:
            raise NotLoggedInError

        user_id = self.user.id  # Cache user_id
        root = self.client.get_folder(all_properties=True)

        def _list_rec(item):
            if item.isfile():
                yield NextcloudFile(id=item.file_id, name=item.basename(), path=item.get_relative_path()[1:], size=item.size, owner=item.owner_id == user_id, shared=None, created_at=None, modified_at=item.last_modified_datetime, file=item)

            if item.isdir():
                for i in item.list(all_properties=True):
                    yield from _list_rec(i)

        yield from _list_rec(root)
