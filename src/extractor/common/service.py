"""
[summary]
"""
from abc import ABC
from abc import abstractmethod
from abc import abstractproperty
from extractor.data import User
from extractor.data import File


class CloudService(ABC):
    """
    Abstract Baseclass for Cloudservices
    """

    @abstractmethod
    def login(self, username, password):
        pass

    @abstractproperty
    def user(self) -> User:
        pass
