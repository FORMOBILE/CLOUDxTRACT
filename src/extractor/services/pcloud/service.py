import logging
from functools import lru_cache

from extractor.common import CloudService
from extractor.data import Folder, User
from extractor.errors import NotLoggedInError

from .client import Client
from .file import PCloudFile

logger = logging.getLogger(__name__)


class PCloudService(CloudService):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.client = None

    def login(self, username: str, password: str) -> User:
        self.client = Client(username, password)
        return self.user

    @property
    def is_logged_in(self):
        return self.client is not None

    @property
    @lru_cache(maxsize=1)
    def user(self) -> User:
        if not self.is_logged_in:
            raise NotLoggedInError

        try:
            data = self.client.userinfo()
        except Exception:
            # TODO
            raise
        else:
            return User(
                id=data["userid"],
                email=data["email"],
            )

    @property
    def files(self):
        yield from [
            node for node in self._iter_tree(self._tree) if isinstance(node, PCloudFile)
        ]

    @property
    def folders(self):
        yield from [
            node
            for node in self._iter_tree(self._tree)
            if isinstance(node, Folder) and not node.name == ""
        ]

    @property
    @lru_cache(maxsize=1)
    def _tree(self):
        if not self.is_logged_in:
            raise NotLoggedInError

        return self._parse_tree(
            self.client.listfolder(folderid=0, recursive=1, showdeleted=0, nofiles=0)[
                "metadata"
            ]
        )

    def _iter_tree(self, node):
        yield node

        if isinstance(node, Folder):
            for item in node.contents:
                yield from self._iter_tree(item)

    def _parse_tree(self, data):
        """ """

        root = self._parse_folder(data)
        return root

    def _parse_file(self, data, parent):
        """ """
        return PCloudFile(
            id=data["fileid"],
            name=data["name"],
            path=parent.path + "/" + data["name"],
            owner=data["ismine"],
            shared=data["isshared"],
            created_at=data["created"],
            modified_at=data["modified"],
            size=data["size"],
            session=self.client,
        )

    def _parse_folder(self, data, parent=None):
        """ """

        if data.get("path") is None:
            if parent is not None and not parent.path == "":
                data.setdefault("path", parent.path + "/" + data["name"])
            else:
                data["path"] = data["name"]

        if data["name"] == "/":
            data["name"] = ""
        if data["path"] == "/":
            data["path"] = ""

        folder = Folder(
            id=data["folderid"],
            name=data["name"],
            path=data["path"],
            owner=data["ismine"],
            shared=data["isshared"],
            created_at=data["created"],
            modified_at=data["modified"],
        )
        folder.contents = []

        for item in data["contents"]:
            if item["isfolder"] is True:
                folder.contents.append(self._parse_folder(item, folder))
            else:
                folder.contents.append(self._parse_file(item, folder))

        return folder
