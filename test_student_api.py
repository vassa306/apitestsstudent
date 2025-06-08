"""
This module handles student API integration tests, including authentication,
requests to the /Students/All endpoint, and response verification.
"""


import unittest
import json
import requests
from ApiResponseWrapper import ApiResponseWrapper
from test_data_helper import TestDataHelper

REQUEST_URL = "https://localhost:7055/api"
headers = {
    "accept": "application/json"
}


def load_payload():
    """ load payload for post request"""
    with open("data.json", "r", encoding="utf-8") as file:
        payload = json.load(file)
    return payload


def load_certificate():
    """ load cert for post request"""
    path = load_payload()
    return path["cert_path"]


def create_url(url, endpoint):
    return f"{url}/{endpoint}"


def load_token() -> str:
    """ get token from post request"""
    try:
        response = requests.post(
            url=create_url(REQUEST_URL, "User"),
            headers=headers,
            json=load_payload(),
            verify=load_certificate(),
            timeout=20
        )
        response.raise_for_status()

    except requests.exceptions.Timeout:
        print("Request timed out.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    try:
        response_data = response.json()
    except ValueError:
        print("Failed to parse JSON response.")
        return None

    if not response_data:
        print("Response data is empty.")
        return None

    token = response_data.get("token")
    return token


def verify_data_in_list(key1, key2, name, data):
    for value in data[key1]:
        if name.lower() in value.get(key2, "").lower():
            return True
    return False


def verify_keys_in_response(data: dict, expected_keys: list[str] = None):
    if expected_keys is None:
        expected_keys = ["status", "statusCode", "data", "errors"]

    missing = [key for key in expected_keys if key not in data]
    assert not missing, f" Missing keys: {missing}"


def verify_errors(response):
    for item in response:
        assert item.get("errors") is None, f"Expected 'errors' to be null, got {item.get('errors')}"


def verify_response_schema(
        data_list: list[dict],
        expected_schema: dict[str, type],
        allow_null: list[str] = None
):
    if allow_null is None:
        allow_null = []

    for index, item in enumerate(data_list):
        for key, expected_type in expected_schema.items():
            assert key in item, f"[Item {index}] Missing key: '{key}'"

            value = item[key]
            if value is None:
                assert key in allow_null, f"[Item {index}] '{key}' is None but not allowed to be"
            else:
                assert isinstance(value, expected_type), (
                    f"[Item {index}] Key '{key}' has wrong type."
                    f" Expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )


class TestStudentApi(unittest.TestCase):
    """
    Test
    suite
    for verifying the / Students API endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.helper = TestDataHelper()
        cls.auth_headers = cls.helper.get_headers()
        cls.cert = cls.helper.get_cert()
        cls.url = cls.helper.get_base_url()
        cls.expected_users = ["vasa", "Jane", "vasik", "pavlik", "pata"]
        cls.token = cls.helper.token
        cls.invalid_name = "Tom"

    def call_api_request(self, endpoint):
        try:
            response = requests.get(
                url=create_url(self.url, endpoint),
                headers=self.auth_headers,
                verify=load_certificate(),
                timeout=10
            )
            return response
        except requests.exceptions.Timeout:
            print(f"Request to {endpoint} timed out.")
            return None

    def test_students_all_endpoint_happy_path(self):
        response = self.call_api_request(endpoint="Students/All")
        self.assertEqual(response.status_code, 200, msg=f"Status: "
                                                        f"{response.status_code}, "
                                                        f"Body: {response.text}")

        data_response = response.json()
        verify_keys_in_response(data_response)
        self.assertTrue(data_response["status"])
        self.assertIsNone(data_response["errors"])

        # Verify all expected names are in the list
        for name in self.expected_users:
            self.assertTrue(
                verify_data_in_list("data", "name", name, data_response),
                msg=f"User with name '{name}' not found"
            )

        self.assertEqual(len(data_response["data"]), 5,
                         f"unexpected length of the list, should be {len(data_response['data'])}")

    def test_students_invalid_name(self):
        invalid_name = self.invalid_name
        response = self.call_api_request("Students/All")
        self.assertEqual(response.status_code, 200, msg=f"Status: {response.status_code}, "
                                                        f"Body: {response.text}")
        data_response = response.json()
        actual_names = [student["name"] for student in data_response["data"]]
        print(actual_names)
        self.assertFalse(invalid_name in actual_names)

    def test_unique_department_ids(self):
        response = self.call_api_request("Students/All")
        print(response)
        data = response.json()["data"]
        department_ids = [item.get("departmentId") for item in data]
        unique_ids = list(set(department_ids))
        self.assertIsInstance(unique_ids, list)

    def test_check_response_scheme(self):
        response = self.call_api_request("Students/All")
        wrapped = ApiResponseWrapper(response)
        print(wrapped.data)
        self.assertEqual(wrapped.status_code, 200)
        self.assertTrue(wrapped.status)
        self.assertIsNone(wrapped.errors)

        schema = {
            "id": int,
            "name": str,
            "email": str,
            "address": str,
            "departmentId": int,
            "departmentName": str
        }

        verify_response_schema(
            data_list=wrapped.data,
            expected_schema=schema,
            allow_null=["departmentId", "departmentName"]
        )


if __name__ == '__main__':
    unittest.main()
