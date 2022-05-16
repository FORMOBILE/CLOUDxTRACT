from dataclasses import dataclass


@dataclass
class User:
    id: any
    username: str = None
    given_name: str = None
    surname: str = None
    displayname: str = None
    email: str = None
    phone: any = None
