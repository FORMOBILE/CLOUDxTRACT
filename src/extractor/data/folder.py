from dataclasses import dataclass
from datetime import datetime


@dataclass
class Folder:
    id: any
    name: str
    path: str
    owner: bool
    shared: bool
    created_at: datetime
    modified_at: datetime
    # contents: any = None

    @property
    def full_path(self):
        return "/".join([self.path, self.name])
