import requests


class Client:
    """Strato Hidrive Client."""

    ENDPOINT_URL = "https://api.hidrive.strato.com/2.1"

    def __init__(self, username, password):
        # store Credentials
        self._username = username
        self._password = password

        # Session
        self._http: requests.Session = None  # Requests session
        self._access_token: str = None

        # Login
        self._login()

    def _login(self) -> None:
        """
        Helpermethod for Login.
        """

        # sending the request to get the token
        response = requests.post(
            "https://my.hidrive.com/auth/login",
            headers={
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Request-With": "XMLHttpRequest",
                "Origin": "https://hidrive.com",
                "DNT": "1",
                "Connection": "keep-alive",
                "Referer": "https://hidrive.com/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            data={"username": self._username, "password": self._password},
        ).json()

        if "access_token" in response:  # check the response
            self._access_token = response["access_token"]  # save the access_token
        else:
            raise Exception("Login failed")

        # Create Session Object for further HTTP-Handling
        session = requests.Session()
        session.headers.update(
            {
                "Content-Type": "application/xml; charset=UTF-8",
                "Authorization": f"Bearer {self._access_token}",
            }
        )
        self._http = session

    def get_user_data(self) -> dict:
        response = self._http.get(
            f"{self.ENDPOINT_URL}/user",
            params={
                "fields": "account,alias,descr,email,email_pending,email_verified,encrypted,folder.id,folder.path,"
                "folder.size,home,home_id,is_admin,is_owner,language,protocols,has_password"
            },
        )
        response.raise_for_status()

        return response.json()[0]

    def download_file_content(self, path: str):
        response = self._http.get(
            f"{self.ENDPOINT_URL}/file", params={"path": path}, stream=True
        )
        response.raise_for_status()

        return response.content

    def get_file_content_stream(self, path: str) -> requests.Response:
        response = self._http.get(
            f"{self.ENDPOINT_URL}/file", params={"path": path}, stream=True
        )
        response.raise_for_status()
        return response

    def get_meta_info(self, path: str) -> dict:  # param = path for the file to check
        response = self._http.get(f"{self.ENDPOINT_URL}/meta", params={"path": path})
        response.raise_for_status()

        return response.json()

    def get_directory(self, path: str = "/") -> dict:
        response = self._http.get(
            f"{self.ENDPOINT_URL}/dir",
            params={
                "path": path,
                "members": "none",
                "fields": "id,name,path,ctime,mtime",
            },
        )
        response.raise_for_status()
        folder_data = response.json()
        # name and path are urlencoded -> urldecode
        folder_data.update(
            {
                "name": requests.utils.unquote(folder_data.get("name")),
                "path": requests.utils.unquote(folder_data.get("path")),
            }
        )

        fetch_chunk_size = 1000  # max 5000
        fetch_start = 0
        fetch_end = fetch_start + fetch_chunk_size
        members = []
        while True:
            response = self._http.get(
                f"{self.ENDPOINT_URL}/dir",
                params={
                    "path": path,
                    "members": "all",
                    "limit": f"{fetch_start},{fetch_end}",
                    "fields": "members.id,members.name,members.path,members.ctime,members.mtime,members.type",
                },
            )
            response.raise_for_status()

            members_data = response.json()
            members.extend(members_data.get("members"))

            if len(members_data.get("members")) == fetch_chunk_size:
                fetch_start = fetch_end
                fetch_end = fetch_end + fetch_chunk_size
            else:
                break

        # name and path are urlencoded -> urldecode
        for member in members:
            member.update(
                {
                    "name": requests.utils.unquote(member.get("name")),
                    "path": requests.utils.unquote(member.get("path")),
                }
            )
        folder_data.update({"members": members})

        return folder_data
