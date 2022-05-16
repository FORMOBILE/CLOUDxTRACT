"""Low-level MediaFire API Client"""

import hashlib
import logging

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class QueryParams(dict):
    """dict tailored for MediaFire requests.

    * won't store None values
    * boolean values are converted to 'yes'/'no'
    """

    def __init__(self, defaults=None):
        super(QueryParams, self).__init__()
        if defaults is not None:
            for key, value in defaults.items():
                self.__setitem__(key, value)

    def __setitem__(self, key, value):
        """Set dict item, handling booleans"""
        if value is not None:
            if value is True:
                value = "yes"
            elif value is False:
                value = "no"
            dict.__setitem__(self, key, value)


class MediaFireApiError(Exception):
    """Base class for API errors"""

    def __init__(self, message, code=None):
        """Initialize exception"""
        self.code = code
        self.message = message
        super(MediaFireApiError, self).__init__(message, code)

    def __str__(self):
        """Stringify exception"""
        return "{}: {}".format(self.code, self.message)


class MediaFireConnectionError(Exception):
    """Low level connection errors"""

    pass


class Client:
    """Low-level HTTP API Client"""

    API_BASE = "https://www.mediafire.com"
    API_VER = "1.5"

    def __init__(self, email, password, app_id="42511"):
        """Initialize MediaFire Client"""

        self.http = requests.Session()
        self.http.mount("https://", HTTPAdapter(max_retries=3))
        self._session = None
        self._action_tokens = {}

        self.login(email, password, app_id)

    @classmethod
    def _build_uri(cls, action):
        """Build endpoint URI from action"""
        return "/api/" + cls.API_VER + "/" + action + ".php"

    def _build_query(self, uri, params=None):
        """Prepare query string"""

        if params is None:
            params = QueryParams()

        params["response_format"] = "json"

        session_token = None

        if self._session:
            session_token = self._session["session_token"]

        if session_token:
            params["session_token"] = session_token

        # make order of parameters predictable for testing
        keys = list(params.keys())
        keys.sort()

        query = urlencode([tuple([key, params[key]]) for key in keys])

        secret_key_mod = int(self._session["secret_key"]) % 256

        signature_base = (
            str(secret_key_mod) + self._session["time"] + uri + "?" + query
        ).encode("ascii")

        query += "&signature=" + hashlib.md5(signature_base).hexdigest()

        return query

    def _process_response(self, response):
        """Parse response"""

        response.raise_for_status()

        # if we are here, then most likely have json
        try:
            response_node = response.json()["response"]
        except ValueError:
            # promised JSON but failed
            raise MediaFireApiError("JSON decode failure")

        if response_node.get("new_key", "no") == "yes":
            self._regenerate_secret_key()

        # check for errors
        if response_node["result"] != "Success":
            raise MediaFireApiError(response_node["message"], response_node["error"])

        return response_node

    def _regenerate_secret_key(self):
        """Regenerate secret key

        http://www.mediafire.com/developers/core_api/1.3/getting_started/#call_signature
        """
        # Don't regenerate the key if we have none
        if self._session and "secret_key" in self._session:
            self._session["secret_key"] = (
                int(self._session["secret_key"]) * 16807
            ) % 2147483647

    def _request(
        self,
        action,
        params=None,
        headers=None,
    ):
        """Perform request to MediaFire API

        action -- "category/name" of method to call
        params -- dict of parameters or query string
        headers -- additional headers to send (used for upload)

        session_token and signature generation/update is handled automatically
        """

        uri = self._build_uri(action)

        if isinstance(params, str):
            query = params
        else:
            query = self._build_query(uri, params)

        if headers is None:
            headers = {}

        data = query
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        try:
            # bytes from now on
            url = (self.API_BASE + uri).encode("utf-8")
            if isinstance(data, str):
                # request's data is bytes, dict, or filehandle
                data = data.encode("utf-8")

            response = self.http.post(url, data=data, headers=headers, stream=True)
        except RequestException as ex:
            raise MediaFireConnectionError("RequestException: {}".format(ex))

        return self._process_response(response)

    @property
    def session(self):
        """Returns current session information"""
        return self._session

    @session.setter
    def session(self, value):
        """Set session token

        value -- dict returned by user/get_session_token"""

        # unset session token
        if value is None:
            self._session = None
            return

        if not isinstance(value, dict):
            raise ValueError("session info is required")

        session_parsed = {}

        for key in ["session_token", "time", "secret_key"]:
            if key not in value:
                raise ValueError("Missing parameter: {}".format(key))
            session_parsed[key] = value[key]

        for key in ["ekey", "pkey"]:
            # nice to have, but not mandatory
            if key in value:
                session_parsed[key] = value[key]

        self._session = session_parsed

    @session.deleter
    def session(self):
        """Unset session"""
        self._session = None

    def login(self, email, password, app_id):
        self.session = self.user_get_session_token(
            app_id=app_id, email=email, password=password, api_key=None
        )

    def user_get_session_token(
        self,
        app_id=None,
        email=None,
        password=None,
        ekey=None,
        fb_access_token=None,
        tw_oauth_token=None,
        tw_oauth_token_secret=None,
        api_key=None,
    ):
        """user/get_session_token

        http://www.mediafire.com/developers/core_api/1.5/user/#get_session_token
        """

        if app_id is None:
            raise ValueError("app_id must be defined")

        params = QueryParams(
            {
                "application_id": str(app_id),
                "token_version": 2,
                "response_format": "json",
            }
        )

        if fb_access_token:
            params["fb_access_token"] = fb_access_token
            signature_keys = ["fb_access_token"]
        elif tw_oauth_token and tw_oauth_token_secret:
            params["tw_oauth_token"] = tw_oauth_token
            params["tw_oauth_token_secret"] = tw_oauth_token_secret
            signature_keys = ["tw_oauth_token", "tw_oauth_token_secret"]
        elif (email or ekey) and password:
            signature_keys = []
            if email:
                signature_keys.append("email")
                params["email"] = email

            if ekey:
                signature_keys.append("ekey")
                params["ekey"] = ekey

            params["password"] = password
            signature_keys.append("password")
        else:
            raise ValueError("Credentials not provided")

        signature_keys.append("application_id")

        signature = hashlib.sha1()
        for key in signature_keys:
            signature.update(str(params[key]).encode("ascii"))

        # Note: If the app uses a callback URL to provide its API key,
        # or if it does not have the "Require Secret Key" option checked,
        # then the API key may be omitted from the signature
        if api_key:
            signature.update(api_key.encode("ascii"))

        query = urlencode(params)
        query += "&signature=" + signature.hexdigest()

        return self._request("user/get_session_token", params=query)

    def user_renew_session_token(self):
        """user/renew_session_token:

        http://www.mediafire.com/developers/core_api/1.3/user/#renew_session_token
        """
        return self._request("user/renew_session_token")

    def user_get_info(self):
        """user/get_info

        http://www.mediafire.com/developers/core_api/1.3/user/#get_info
        """
        return self._request("user/get_info")

    def folder_get_depth(self, folder_key=None):
        """folder/get_depth

        http://www.mediafire.com/developers/core_api/1.3/folder/#get_depth
        """
        return self._request(
            "folder/get_depth", QueryParams({"folder_key": folder_key})
        )

    def folder_get_info(self, folder_key=None, device_id=None, details=None):
        """folder/get_info

        http://www.mediafire.com/developers/core_api/1.3/folder/#get_info
        """
        return self._request(
            "folder/get_info",
            QueryParams(
                {"folder_key": folder_key, "device_id": device_id, "details": details}
            ),
        )

    def folder_get_content(
        self,
        folder_key=None,
        content_type=None,
        filter_=None,
        device_id=None,
        order_by=None,
        order_direction=None,
        chunk=None,
        details=None,
        chunk_size=None,
    ):
        """folder/get_content

        http://www.mediafire.com/developers/core_api/1.3/folder/#get_content
        """
        return self._request(
            "folder/get_content",
            QueryParams(
                {
                    "folder_key": folder_key,
                    "content_type": content_type,
                    "filter": filter_,
                    "device_id": device_id,
                    "order_by": order_by,
                    "order_direction": order_direction,
                    "chunk": chunk,
                    "details": details,
                    "chunk_size": chunk_size,
                }
            ),
        )

    def file_get_info(self, quick_key=None):
        """file/get_info

        http://www.mediafire.com/developers/core_api/1.3/file/#get_info
        """
        return self._request("file/get_info", QueryParams({"quick_key": quick_key}))

    def file_get_links(self, quick_key, link_type=None):
        """file/get_links

        http://www.mediafire.com/developers/core_api/1.3/file/#get_links
        """
        return self._request(
            "file/get_links",
            QueryParams(
                {
                    "quick_key": quick_key,
                    "link_type": link_type,
                }
            ),
        )
