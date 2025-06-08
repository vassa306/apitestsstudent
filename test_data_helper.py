""" Helper for api tests"""

import json
import requests
from main import create_url


class TestDataHelper:
    """Test Data helper for Api testing """

    BASE_URL = "https://localhost:7055/api"
    APP_TYPE = "application/json"

    def __init__(self, data_file="data.json"):
        with open(data_file, "r", encoding="utf8") as file:
            self.data = json.load(file)

        self.base_url = self.BASE_URL
        self.cert_path = self.data["cert_path"]
        self.expected_users = self.data.get("expected_users", [])
        self.token = self._get_token()
        self.authentication_headers = self.get_headers()
        self.app_type = self.APP_TYPE

    def _get_token(self):
        login_payload = {
            "policy": self.data["policy"],
            "email": self.data["email"],
            "password": self.data["password"]

        }
        print()
        headers = {"accept": "application/json"}
        response = requests.post(
            url=create_url(self.base_url, "User"),
            headers=headers,
            json=login_payload,
            verify=self.cert_path,
            timeout=20
        )
        print("Response body:", response.text)
        response.raise_for_status()
        return response.json().get("token")

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": self.APP_TYPE
        }

    def get_cert(self):
        return self.cert_path

    def get_expected_users(self):
        return self.expected_users

    def get_base_url(self):
        return self.base_url
