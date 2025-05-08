import requests
import json

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


def test_get_request(expected_users):
    token = loadToken()
    req_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    response = requests.get(url=create_url(request_url, endpoint='Students/All'), headers=req_headers,
                            verify=load_certificate())

    data_response = response.json()

    assert data_response is not  None
    assert response.status_code == 200
    all_present = True
    for expected_name in expected_users:
        is_present = verify_data_in_list(key1="data", key2="name", name=expected_name, data=data_response)
        if not is_present:
            all_present = False
    users_count = len(data_response['data'])

    verify_keys_in_response(data=data_response, expected_keys=["status", "statusCode", "data", "errors"])
    assert data_response.get("status") is True
    assert data_response.get("errors") is None
    assert users_count == 5
    assert all_present, "Some items missing in list"
