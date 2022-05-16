import logging
import requests
from hashlib import sha1
from extractor.common.tools import RequiredParameterCheck
from extractor.errors import LoginError

logger = logging.getLogger(__name__)


class Client:

    endpoint = None
    endpoint_us = "https://api.pcloud.com/"
    endpoint_eu = "https://eapi.pcloud.com/"

    def __init__(self, username, password):
        self.username = username.lower()
        self.password = password
        self.endpoint = self.endpoint_us
        self.session = requests.Session()
        self.auth_token = self.get_auth_token()

    def _do_request(self, method, authenticate=True, json=True, stream=False, **kw):
        if authenticate:
            params = {"auth": self.auth_token}
        else:
            params = {}
        params.update(kw)

        resp = self.session.get(self.endpoint + method, params=params, stream=stream)
        if stream:
            return resp
        elif json:
            return resp.json()
        else:
            return resp.content

    # Authentication
    def getdigest(self):
        resp = self._do_request("getdigest", authenticate=False)
        return bytes(resp["digest"], "utf-8")

    def get_auth_token(self):
        digest = self.getdigest()
        passworddigest = sha1(
            self.password.encode("utf-8")
            + bytes(sha1(self.username.encode("utf-8")).hexdigest(), "utf-8")
            + digest
        )
        params = {
            "getauth": 1,
            "logout": 1,
            "username": self.username,
            "digest": digest.decode("utf-8"),
            "passworddigest": passworddigest.hexdigest(),
        }
        resp = self._do_request("userinfo", authenticate=False, **params)
        if "auth" not in resp:
            # Try change Endpoint from US to EU
            if self.endpoint == self.endpoint_us:
                self.endpoint = self.endpoint_eu
                return self.get_auth_token()
            else:
                self.endpoint = self.endpoint_us
                raise LoginError(resp["error"])

        return resp["auth"]

    # User
    def userinfo(self, **kwargs):
        return self._do_request("userinfo", **kwargs)

    # Folders
    @RequiredParameterCheck(("path", "folderid"))
    def listfolder(self, **kwargs):
        return self._do_request("listfolder", **kwargs)

    @RequiredParameterCheck(("path", "fileid"))
    def checksumfile(self, **kwargs):
        return self._do_request("checksumfile", **kwargs)

    # Auth API methods
    def logout(self, **kwargs):
        return self._do_request("logout", **kwargs)

    # File API methods
    @RequiredParameterCheck(("path", "fileid"))
    def stat(self, **kwargs):
        return self._do_request("stat", **kwargs)

    @RequiredParameterCheck(("flags",))
    def file_open(self, **kwargs):
        return self._do_request("file_open", **kwargs)

    @RequiredParameterCheck(("fd",))
    def file_read(self, **kwargs):
        return self._do_request("file_read", json=False, **kwargs)

    @RequiredParameterCheck(("fd",))
    def file_pread(self, **kwargs):
        return self._do_request("file_pread", json=False, **kwargs)

    @RequiredParameterCheck(("fd",))
    def file_size(self, **kwargs):
        return self._do_request("file_size", **kwargs)

    @RequiredParameterCheck(("fd",))
    def file_checksum(self, **kwargs):
        return self._do_request("file_checksum", **kwargs)

    @RequiredParameterCheck(("fd",))
    def file_close(self, **kwargs):
        return self._do_request("file_close", **kwargs)

    @RequiredParameterCheck(("fd",))
    def file_lock(self, **kwargs):
        return self._do_request("file_lock", **kwargs)
