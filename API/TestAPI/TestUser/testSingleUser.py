import pytest
import random
from os  import path
from pathlib import Path
from http.cookies import SimpleCookie
from fastapi.testclient import TestClient

from API.TestAPI.TestUser.testUserData import USERS, UPDATE_USERNAME_STRING, UPDATE_PASSWORD_STRING,\
     UPDATE_XML_DIR, UPDATE_XML_FILE, UPDATE_HTML_DIR, UPDATE_HTML_FILE, UPDATE_ICON_DIR, UPDATE_ICON_FILE

from main import app

client = TestClient(app)

single_user = USERS[ random.randrange(len(USERS)) ]
pytest.USER_AUTH = None

@pytest.mark.parametrize(
    "email, username, password, expected_codes, fail_message", [
    (single_user["email"], single_user["username"], "",       [409, 422], "Registered empty password"),
    (single_user["email"], single_user["username"], "1234",   [409, 422], "Registered too short password"),
    (single_user["email"], single_user["username"], "1" * 51, [409, 422], "Registered too long password"),
    (single_user["email"], "",                "1" * 51, [409, 422], "Registered empty username and too long password"),
    (single_user["email"], "",                  "1234", [409, 422], "Registered empty username and short password"),
    (single_user["email"], "short",             "1234", [409, 422], "Registered short username and password"),
    ("",       single_user["username"], single_user["password"], [409, 422], "Registered empty email"),
    ("a" * 20, single_user["username"], single_user["password"], [409, 422], "Registered a non email"),
    (("a" * 80) + "@" + ("b" * 20) + ".com", single_user["username"], single_user["password"], [409, 422], "Registered a long email"),
    (single_user["email"],                   single_user["username"], single_user["password"], [201], "Couldn't register user")
])
def test_register(email, username, password, expected_codes, fail_message):
    response = client.post(
        "/user/register/",
        headers = { "accept": "application/json" },
        json    = { "email": email, "username": username, "password": password }
    )
    assert response.status_code in expected_codes, fail_message + ": " + response.content.decode()

@pytest.mark.parametrize(
    "email, password, expected_codes, fail_message", [
    ("", single_user["password"], [401, 422], "Login with empty email"),
    (single_user["email"], "",    [401, 422], "Login with empty password"),
    (single_user["email"], single_user["password"], [200], "Couldn't login user")
])
def test_login(email, password, expected_codes, fail_message):
    response = client.post(
        "/user/login/",
        headers = { "accept": "application/json" },
        data = { "email": email, "password": password }
    )
    assert response.status_code in expected_codes, fail_message + f'\nError: {response.content.decode()}'
    if response.status_code == 200 and response.headers["Authorization"]:
        pytest.USER_AUTH = response.headers["Authorization"]

def test_update_username():
    
    response = client.put(
        "/user/update/username/",
        headers = { "accept": "application/json", "Authorization": pytest.USER_AUTH },
        json = { "email": single_user["email"], "new_username": single_user["username"] + UPDATE_USERNAME_STRING, "password": single_user["password"] }
    )
    assert response.status_code == 200, f'Error: {response.content.decode()} && Authorization: {pytest.USER_AUTH}\n'

@pytest.mark.parametrize(
    "email, old_password, new_password, expected_codes, fail_message", [
    (single_user["email"], single_user["password"], single_user["password"],     [400, 401, 403], "Password updated with new password being equal to old password"),
    (single_user["email"], "", single_user["password"] + UPDATE_PASSWORD_STRING, [400, 401, 403], "Password updated with wrong user password"),
    (single_user["email"], single_user["password"], single_user["password"] + UPDATE_PASSWORD_STRING, [200], "Password should have been updated")
])
def test_update_password(email, old_password, new_password, expected_codes, fail_message):
    response = client.put(
        "/user/update/password/",
        headers = { "accept": "application/json", "Authorization": pytest.USER_AUTH },
        json = { "email": email, "old_password": old_password, "new_password": new_password }
    )
    assert response.status_code in expected_codes, fail_message

json_upload_file_fail    = {'detail': 'Failed to update icon. Formats allowed: jpeg, png, bmp, webp'}
json_upload_file_success = { "email": single_user["email"], "result": "success" }

@pytest.mark.parametrize(
    "email, password, dir_file, file, expected_codes, fail_message, compare_message", [
    (single_user["email"], single_user["password"] + UPDATE_PASSWORD_STRING, UPDATE_XML_DIR,  UPDATE_XML_FILE,  [400, 401, 403], "Uploaded xml", json_upload_file_fail),
    (single_user["email"], single_user["password"] + UPDATE_PASSWORD_STRING, UPDATE_HTML_DIR, UPDATE_HTML_FILE, [400, 401, 403], "Uploaded html", json_upload_file_fail),
    (single_user["email"], single_user["password"] + UPDATE_PASSWORD_STRING, UPDATE_ICON_DIR, UPDATE_ICON_FILE, [200] , "Didn't upload the jpeg file", json_upload_file_success)
])
def test_update_icon(email, password, dir_file, file, expected_codes, fail_message, compare_message):

    file_to_upload = open(path.join(path.dirname(__file__), dir_file, file) , "rb")
    
    response = client.put(
        "/user/update/icon/",
        headers = { "accept": "application/json", "Authorization": pytest.USER_AUTH },
        data = { "email": email, "password": password },
        files = { "new_icon": (file, file_to_upload, "image/jpeg") }
    )
    file_to_upload.close()
    assert response.status_code in expected_codes, f'Error: {response.content.decode()}\n'
    assert response.json() == compare_message

def test_profile():
    response = client.get(
        "/user/profile/",
        headers = { "accept": "application/json", "Authorization": pytest.USER_AUTH },
    )
    assert response.status_code == 200, f'Error: {response.content.decode()}\n'

def test_logout():
    response = client.post(
        "/user/logout/",
        headers = { "accept": "application/json", "Authorization": pytest.USER_AUTH },
    )
    assert response.status_code == 200, f'Error: {response.content.decode()}\n'
    assert response.json() == { "email": single_user["email"], "result": "success" }

def test_profile_after_logout():
    
    response = client.get(
        "/user/profile/",
        headers = { "accept": "application/json", "Authorization": pytest.USER_AUTH },
    )
    assert response.status_code in [400, 401, 403, 422], f'Error: {response.content.decode()}\n'

""" Running with python3.8 -m pytest -s API/TestAPI/TestUser/<this_file_name>
"""
print('If you\'re running this file alone and not deleting the DB you can check for the user with:')
print(f'"email": {single_user["email"]}')
print(f'"username": {single_user["username"] + UPDATE_USERNAME_STRING}')
print(f'"password": {single_user["password"] + UPDATE_PASSWORD_STRING}')
