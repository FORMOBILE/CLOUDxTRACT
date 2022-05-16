from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class File(ABC):
    id: any
    name: str
    path: str
    size: int
    owner: bool
    shared: bool
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    @abstractmethod
    def __enter__(self):
        ...

    @abstractmethod
    def __exit__(self, exception_type, exception_value, exception_traceback):
        ...
