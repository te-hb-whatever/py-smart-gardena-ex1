import requests
import json

from gardena.location import Location


class SmartSystem:
    """Base class to communicate with gardena and handle network calls"""

    def __init__(self, email=None, password=None, debug=False):
        """Constructor, create instance of gateway"""
        if email is None or password is None:
            raise ValueError("Arguments 'email' and 'passwords' are required")
        self.debug = debug
        self.email = email
        self.password = password
        self.token = None
        self.refresh_token = None
        self.user_id = None
        self.request_session = requests.session()
        self.locations = None

    def create_header(self):
        headers = {"Content-Type": "application/json"}
        if self.token is not None:
            headers["X-Session"] = self.token
        return headers

    def authenticate(self):
        """
        Authenticate and get tokens.
        This function needs to be called first.
        """
        url = "https://smart.gardena.com/sg-1/sessions"
        credentials = {"email": self.email, "password": self.password}
        response = self.request_session.post(
            url,
            headers=self.create_header(),
            data=json.dumps(credentials, ensure_ascii=False),
        )
        response.raise_for_status()
        response_data = json.loads(response.content.decode("utf-8"))
        self.token = response_data["sessions"]["token"]
        self.user_id = response_data["sessions"]["user_id"]

    def update_locations(self):
        """Update locations (gardens, ..) """
        url = "https://smart.gardena.com/sg-1/locations/"
        params = (("user_id", self.user_id),)
        response = self.request_session.get(
            url, headers=self.create_header(), params=params
        )
        response.raise_for_status()
        response_data = json.loads(response.content.decode("utf-8"))
        self.locations = {}
        for location in response_data["locations"]:
            if location["id"] not in self.locations:
                self.locations[location["id"]] = Location(smart_system=self)
            self.locations[location["id"]].update_information(location)

    def get_session(self):
        return self.request_session
