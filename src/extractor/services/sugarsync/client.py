from typing import List
from datetime import datetime
from functools import lru_cache

import pytz
import requests
from requests.exceptions import RequestException
from xmltodict import parse as xml_to_dict
from xmltodict import unparse as dict_to_xml


class Client:
    """SugarSync Client."""

    def __init__(self, app_id, app_access_key, app_private_key, username, password):
        # App
        self._app_id = app_id
        self._app_access_key = app_access_key
        self._app_private_key = app_private_key

        # User
        self._user = None
        self._user_ressource_url = None

        # Session
        self._http = None
        self._refresh_token = None
        self._access_token = None
        self._access_token_expires_at = None

        # Login
        self._login(username, password)

    def _login(self, username, password):
        """
        Helperfunction for Login.

        See https://www.sugarsync.com/dev/get-auth-token-example.html

        Args:
            username (str): Username
            password (str): Password
        """
        # Fetch Refresh Token
        refresh_token = self.get_refresh_token(
            self._app_id,
            self._app_access_key,
            self._app_private_key,
            username,
            password,
        )
        self._refresh_token = refresh_token

        # Fetch Access Token
        access_token, expires_at, user_ressource_url = self.get_access_token(
            self._app_access_key, self._app_private_key, refresh_token
        )
        self._access_token = access_token
        self._access_token_expires_at = expires_at
        self._user_ressource_url = user_ressource_url

        # Create Session Object for further HTTP-Handling
        session = requests.Session()
        session.headers.update(
            {
                "Content-Type": "application/xml; charset=UTF-8",
                "Authorization": access_token,
            }
        )
        self._http = session

    @staticmethod
    def get_refresh_token(app_id, app_access_key, app_private_key, username, password):
        """
        Get RefreshToken by Username/Password.

        https://www.sugarsync.com/dev/api/method/create-refresh-token.html
        """
        response = requests.post(
            "https://api.sugarsync.com/app-authorization",
            headers={"Content-Type": "application/xml; charset=UTF-8"},
            data=dict_to_xml(
                {
                    "appAuthorization": {
                        "username": username,
                        "password": password,
                        "application": app_id,
                        "accessKeyId": app_access_key,
                        "privateAccessKey": app_private_key,
                    }
                }
            ).encode("utf-8"),
        )
        response.raise_for_status()

        return response.headers.get("Location")

    @staticmethod
    def get_access_token(app_access_key, app_private_key, refresh_token):
        """
        Refresh the AccessToken.

        See https://www.sugarsync.com/dev/api/method/create-auth-token.html

        Args:
            app_access_key (str): App Access Key
            app_private_key (str): App Private Key
            refresh_token (str): Refresh Token

        Returns:
            str: Access Token
            datetime: Access Token expires At
            str: Ressource URL for the logged in User
        """
        try:
            response = requests.post(
                "https://api.sugarsync.com/authorization",
                headers={"Content-Type": "application/xml; charset=UTF-8"},
                data=dict_to_xml(
                    {
                        "tokenAuthRequest": {
                            "accessKeyId": app_access_key,
                            "privateAccessKey": app_private_key,
                            "refreshToken": refresh_token,
                        }
                    }
                ).encode("utf-8"),
            )
            response.raise_for_status()

            access_token = response.headers.get("Location")
            data = xml_to_dict(response.text)
            user_ressource_url = data["authorization"]["user"]
            expires_at = datetime.fromisoformat(
                data["authorization"]["expiration"]
            ).astimezone(pytz.utc)
        except Exception as ex:
            raise ex

        return access_token, expires_at, user_ressource_url

    @property
    def user(self):
        if self._user is None:
            self._user = self.get_user_by_url(self._user_ressource_url)

        return self._user

    @lru_cache(maxsize=None)
    def get_user_by_url(self, url) -> dict:
        """
        Gets a UserInformation by it's Ressource URL
        See https://www.sugarsync.com/dev/api/method/get-user-info.html

        Args:
            url (str): Ressource URL of the UserInformation (eq. https://api.sugarsync.com/user/123)

        Returns:
            UserInformation: SugarSync UserInformation
        """

        try:
            response = self._http.get(url)
            response.raise_for_status()

            data = xml_to_dict(response.text)["user"]
            data.update({"ref": url})
        except RequestException:
            # Error while HTTP
            raise
        except Exception as ex:
            # Error while convert XML to Dict or something else
            raise ex

        return data

    def get_user_by_id(self, id_) -> dict:
        """
        Get a User by it's Id
        See https://www.sugarsync.com/dev/api/method/get-user-info.html

        Args:
            id (int): SugarSync UserId

        Returns:
            UserInformation: SugarSync UserInformation
        """

        return self.get_user_by_url(f"https://api.sugarsync.com/user/{id_}")

    @lru_cache(maxsize=None)
    def get_contact_by_url(self, url) -> dict:
        """
        Gets a ContactInformation
        See https://www.sugarsync.com/dev/api/method/get-contacts.html

        Args:
            url (str): Ressource URL of the UserInformation
                       (eq. https://api.sugarsync.com/contact/1234/1234)

        Returns:
            Contact: SugarSync Contact Information
        """

        try:
            response = self._http.get(url)
            response.raise_for_status()

            data = xml_to_dict(response.text)["contact"]
            data.update({"ressourceUrl": url})
        except RequestException:
            # Error while HTTP
            raise
        except Exception as ex:
            # Error while convert XML to Dict or something else
            raise ex

        return data

    def get_folder(self, id_):
        id_ = id_.replace("/", ":")
        return self.get_folder_by_url(f"https://api.sugarsync.com/folder/{id_}")

    @lru_cache(maxsize=None)
    def get_folder_by_url(self, url) -> dict:
        try:
            response = self._http.get(url)
            response.raise_for_status()

            response_data = xml_to_dict(response.text)["folder"]
        except RequestException:
            raise
        except Exception as ex:
            raise ex

        return response_data

    def get_folder_contents(self, id_):
        """
        Retrieve the Folder Content

        Args:
            id (string): Folder Id (e.g. /sc/1234/5)

        Returns:
            [type]: [description]
        """

        id_ = id_.replace("/", ":")
        url = f"https://api.sugarsync.com/folder/{id_}/contents"

        return self.get_folder_contents_by_url(url)

    def get_folder_contents_by_url(self, url):
        """
        Fetch the Folder Contents

        Args:
            url (str): [description]

        Yields:
            (Folder|File): [description]
        """

        start = 0
        max_entries = 250
        finished = False

        while not finished:
            # Fetch SyncFolder Collection
            try:
                response = self._http.get(
                    url,
                    params={"start": start, "max": max_entries},
                )
                response.raise_for_status()

                response_data = xml_to_dict(response.text)

                # Handle Files
                files = response_data["collectionContents"].get("file", [])
                if not isinstance(files, list):
                    files = [files]
                for file in files:
                    yield self.get_file_by_url(file["ref"])

                # Handle Folders
                folders = response_data["collectionContents"].get("collection", [])
                if not isinstance(folders, list):
                    folders = [folders]

                for folder in folders:
                    yield self.get_folder_by_url(folder["ref"])

                # Check if more Folders available
                if response_data["collectionContents"]["@hasMore"] == "true":
                    start = start + max_entries
                else:
                    finished = True

            except RequestException as ex:
                raise ex
            except Exception as ex:
                raise ex

    def get_file(self, id_):
        id_ = id_.replace("/", ":")
        return self.get_file_by_url(f"https://api.sugarsync.com/file/{id_}")

    @lru_cache(maxsize=None)
    def get_file_by_url(self, url) -> dict:
        """

        See https://www.sugarsync.com/dev/api/method/get-file-info.html

        Args:
            url ([type]): [description]
        """
        try:
            response = self._http.get(url)
            response.raise_for_status()

            response_data = xml_to_dict(response.text)["file"]
        except RequestException as ex:
            raise ex
        except Exception as ex:
            raise ex

        return response_data

    def get_file_content_stream(self, id_):
        id_ = id_.replace("/", ":")
        return self.get_file_content_stream_by_url(
            f"https://api.sugarsync.com/file/{id_}/data"
        )

    def get_file_content_stream_by_url(self, url):
        response = self._http.get(url, stream=True)
        response.raise_for_status()

        return response

    def get_syncfolders(self) -> List[dict]:
        """
        Get the Sync Folders (Root Folders)
        See https://www.sugarsync.com/dev/api/method/get-syncfolders.html

        Yields:
            Folder: Folder Ressource
        """

        start = 0
        count = 250
        finished = False

        while not finished:
            # Fetch SyncFolder Collection
            try:
                response = self._http.get(
                    self.user.get("syncfolders"),
                    params={"start": start, "max": count},
                )
                response.raise_for_status()

                response_data = xml_to_dict(response.text)
                folders = response_data["collectionContents"]["collection"]
                if not isinstance(folders, list):
                    folders = [folders]

                for folder in folders:
                    yield self.get_folder_by_url(folder["ref"])

                # Check if more Folders available
                if response_data["collectionContents"]["@hasMore"] == "true":
                    start = start + count
                else:
                    finished = True

            except RequestException as ex:
                raise ex
            except Exception as ex:
                raise ex
