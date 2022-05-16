class AuthentificationError(Exception):
    pass


class NotLoggedInError(AuthentificationError):
    pass


class LoginError(AuthentificationError):
    pass


class DownloadError(Exception):
    pass
