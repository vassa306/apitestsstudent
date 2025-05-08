import unittest
import json
import requests

from ApiResponseWrapper import ApiResponseWrapper
from TestDataHelper import TestDataHelper

request_url = "https://localhost:7055/api"
headers = {
    "accept": "application/json"
}


def load_payload():
    with open("data.json", "r") as file:
        payload = json.load(file)
    return payload


def load_certificate():
    path = load_payload()
    return path["cert_path"]


def create_url(url, endpoint):
    return f"{url}/{endpoint}"


def loadToken() -> str:
    response = requests.post(url=create_url(request_url, "User"), headers=headers, json=load_payload(),
                             verify=load_certificate())
    response_data = response.json()
    print(response_data)

    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return ""

    if not response_data:
        print("response data is empty")

    token = response_data.get("token")
    return token


def verify_data_in_list(key1, key2, name, data):
    for value in data[key1]:
        if name.lower() in value.get(key2, "").lower():
            return True
    print(f"Found '{name}' in: {value.get(key2)}")
    return False


def verify_keys_in_response(data: dict, expected_keys: list[str] = None):
    if expected_keys is None:
        expected_keys = ["status", "statusCode", "data", "errors"]

    missing = [key for key in expected_keys if key not in data]
    assert not missing, f" Missing keys: {missing}"


def verify_errors(response):
    for item in response:
        assert item.get("errors") is None, f"Expected 'errors' to be null, got {item.get('errors')}"


def create_url(url, endpoint):
    return f"{url}/{endpoint}"


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
                    f"[Item {index}] Key '{key}' has wrong type. Expected {expected_type.__name__}, got {type(value).__name__}"
                )


class TestStudentApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helper = TestDataHelper()
        cls.auth_headers = cls.helper.get_headers()
        cls.cert = cls.helper.get_cert()
        cls.url = cls.helper.get_base_url()
        cls.expected_users = ["vasa", "Jane", "vasik", "pavlik", "pata"]
        cls.token = cls.helper.token

    def test_students_all_endpoint(self):
        response = requests.get(
            url=create_url(self.url, "Students/All"),
            headers=self.auth_headers,
            verify=load_certificate()
        )
        self.assertEqual(response.status_code, 200, msg=f"Status: {response.status_code}, Body: {response.text}")

        data_response = response.json()
        print(data_response)
        verify_keys_in_response(data_response)
        self.assertTrue(data_response["status"])
        self.assertIsNone(data_response["errors"])

        # Verify all expected names are in the list
        for name in self.expected_users:
            self.assertTrue(
                verify_data_in_list("data", "name", name, data_response),
                msg=f"User with name '{name}' not found"
            )

        self.assertEqual(len(data_response["data"]), 5)

    def test_unique_department_ids(self):
        response = requests.get(
            url=create_url(self.url, "Students/All"),
            headers=self.auth_headers,
            verify=load_certificate()
        )
        print(response)
        data = response.json()["data"]
        department_ids = [item.get("departmentId") for item in data]
        unique_ids = list(set(department_ids))
        self.assertIsInstance(unique_ids, list)  # Just example check

    def test_check_response_scheme(self):
        response = requests.get(
            url=create_url(self.url, "Students/All"),
            headers=self.auth_headers,
            verify=load_certificate()
        )
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
