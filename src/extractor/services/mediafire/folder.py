from dataclasses import dataclass, field
from extractor.data import Folder
from extractor.services.mediafire.file import MediafireFile
from extractor.services.mediafire.client import Client


@dataclass
class MediafireFolder(Folder):
    session: Client = field(compare=False, hash=False, repr=False)

    # @property
    # def path(self):
    #     if "path" not in self._data:
    #         if self.id in ["myfiles", None]:
    #             self._data["path"] = ""
    #         else:
    #             response = self.adapter.client.folder_get_depth(self.id)
    #             depth = response["folder_depth"]
    #             parents = list(map(lambda f: f.get("name"), depth["chain_folders"]))
    #             parents.reverse()
    #             parents.pop()
    #             self._data["path"] = "/".join(parents)

    #     return self._data["path"]

    # @property
    # def file_count(self):
    #     return self._data["file_count"]

    # @property
    # def folder_count(self):
    #     return self._data["folder_count"]

    # @property
    # def revision(self):
    #     return self._data["revision"]

    @property
    def folders(self):
        more_chunks = True
        chunk = 0
        while more_chunks:
            chunk += 1
            content = self.session.folder_get_content(
                content_type="folders",
                chunk=chunk,
                chunk_size=1000,
                folder_key=self.id,
            )["folder_content"]

            # empty folder/file list
            if not content["folders"]:
                break

            # no next page
            if content["more_chunks"] == "no":
                more_chunks = False

            # Iterate through all folders
            for directory_info in content["folders"]:

                if self.path == "":
                    path = directory_info["name"]
                else:
                    path = "/".join(
                        [
                            self.path,
                            directory_info["name"],
                        ]
                    )

                data = {
                    "id": directory_info["folderkey"],
                    "name": directory_info["name"],
                    "path": path,
                    "owner": True,
                    "shared": False,
                    "created_at": None,
                    "modified_at": None,
                    "session": self.session,
                }

                yield MediafireFolder(**data)

    @property
    def files(self):
        more_chunks = True
        chunk = 0
        while more_chunks:
            chunk += 1
            content = self.session.folder_get_content(
                content_type="files",
                chunk=chunk,
                chunk_size=1000,
                folder_key=self.id,
            )["folder_content"]

            # empty folder/file list
            if not content["files"]:
                break

            # no next page
            if content["more_chunks"] == "no":
                more_chunks = False

            for file_info in content["files"]:
                file_info["path"] = "/".join([self.path, file_info["filename"]])
                data = {
                    "session": self.session,
                    "id": file_info["quickkey"],
                    "name": file_info["filename"],
                    "path": file_info["path"],
                    "size": file_info["size"],
                    "owner": True,
                    "shared": False,
                    "created_at": file_info["created_utc"],
                    "modified_at": None,
                    "link": None,
                }
                yield MediafireFile(**data)
