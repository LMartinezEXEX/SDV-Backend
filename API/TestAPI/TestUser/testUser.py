import pytest
from os  import path
from http.cookies import SimpleCookie
from fastapi.testclient import TestClient

from API.TestAPI.TestUser.testUserData import users, \
    UPDATE_USERNAME_STRING, UPDATE_PASSWORD_STRING, UPDATE_ICON_DIR, UPDATE_ICON_FILE

from main import app

client = TestClient(app)

""" Guardamos lo que nos haga falta para interactuar autenticados en un diccionario.
    El diccionario tendría la "forma": "user_email" : (status_code_login, cookie)
"""
USERS_AUTH_DICT = {}

"""
Endpoint test: "/user/register/"

Descripción:
Tiene que funcionar la primera vez que lo ejecutan. Si lo ejecutan una segunda vez no funciona, 
ya que el recurso ha sido creado.

Escenario exitoso: 201 Created
Error: 409 Conflict

"""
def test_register_users(users):
    for user in users:
        user_register = { "email": user["email"], "username": user["username"], "password": user["password"] }
        response = client.post(
            "/user/register/",
            headers = { "accept": "application/json" },
            json    = user_register
        )
        
        assert response.status_code == 201, f'Conflict with {user_register["email"]}'

"""
Endpoint test: "/user/profile/{email}"

Descripción:
Una vez registrados nuestros usuarios, testeamos si son accesibles por un query.

Escenario exitoso: 200 Ok
Error: 404 Not Found

"""
def test_get_users(users):
    for user in users:
        response = client.get(
            "/user/profile/" + user["email"],
            headers = { "accept": "application/json" }
        )

        assert response.status_code == 200, f'User Not Found: {response.content.decode()}\n'


"""
Endpoint test: "/user/login/"

Descripción:
Queremos ver que nos devuelva la información acordada respecto a la autenticación.

Escenario exitoso: 200 Ok
Error: 401 Unauthorized

"""
def test_login_users(users):
    for user in users:
        user_data = { "email": user["email"], "password": user["password"] }
        response = client.post(
            "/user/login/",
            headers = { "accept": "application/json", "content-type": "application/x-www-form-urlencoded" },
            data = user_data
        )

        assert response.status_code == 200, f'Unauthorized: {user["email"]}\n'

        USERS_AUTH_DICT.update({ user_data["email"]: ( response.status_code, response.headers["Authorization"] ) })
    
    for key in list(USERS_AUTH_DICT.keys()):
        if USERS_AUTH_DICT[key][0] == 200:
            print(f'Login: {key} -> {USERS_AUTH_DICT[key][1]}')

"""
Endpoint test: "/user/profile/"

Descripción:
Un usuario puede revisar su perfil exitosamente.

Escenario exitoso: 200 Ok
Error: 400 Bad Request, 401 Unauthorized, 403 Forbidden

"""
def test_profile_users(users):
    for user in users:
        authorization = USERS_AUTH_DICT[user["email"]][1]

        response = client.get(
            "/user/profile/",
            headers = { "accept": "application/json", "Authorization": authorization }
        )

        assert response.status_code == 200, f'Error {user["email"]}: {response.content.decode()}\n'

"""
Endpoint test: "/user/update/username/"

Descripción:
Un usuario puede cambiar su nombre.

Escenario exitoso: 200 Ok
Error: 400 Bad Request, 401 Unauthorized, 403 Forbidden

"""
def test_update_usernames(users):
    for user in users:
        authorization = USERS_AUTH_DICT[user["email"]][1]

        user_data = { "email": user["email"], "new_username": user["username"] + UPDATE_USERNAME_STRING, "password": user["password"] }
        response = client.put(
            "/user/update/username/",
            headers = { "accept": "application/json", "Authorization": authorization },
            json = user_data
        )
        
        assert response.status_code == 200, f'Error {user["email"]}: {response.content.decode()}\n'
        assert response.json() == { "email": user["email"], "result": "success" }

"""
Endpoint test: "/user/update/password/"

Descripción:
Un usuario puede cambiar su password.

Escenario exitoso: 200 Ok
Error: 400 Bad Request, 401 Unauthorized, 403 Forbidden

"""
def test_update_passwords(users):
    for user in users:
        authorization = USERS_AUTH_DICT[user["email"]][1]
        
        user_data = { "email": user["email"], "old_password": user["password"], "new_password": user["password"] + UPDATE_PASSWORD_STRING }
        response = client.put(
            "/user/update/password/",
            headers = { "accept": "application/json", "Authorization": authorization },
            json = user_data
        )

        assert response.status_code == 200, f'Error {user["email"]}: {response.content.decode()}\n'
        assert response.json() == { "email": user["email"], "result": "success" }

"""
Endpoint test: "/user/update/icon/"

Descripción:
Un usuario puede cambiar su icon.

Escenario exitoso: 200 Ok
Error: 400 Bad Request, 401 Unauthorized, 403 Forbidden

"""
def test_update_icons(users):
    for user in users:
        authorization = USERS_AUTH_DICT[user["email"]][1]

        user_data = { "email": user["email"], "password": user["password"] + UPDATE_PASSWORD_STRING }
        file_to_upload = open(path.join(path.dirname(__file__), UPDATE_ICON_DIR, UPDATE_ICON_FILE), "rb")

        response = client.put(
            "/user/update/icon/",
            headers = { "accept": "application/json", "Authorization": authorization },
            data = user_data,
            files = { "new_icon": (UPDATE_ICON_FILE, file_to_upload, "image/jpeg") }
        )
        file_to_upload.close()
        assert response.status_code == 200, f'Error {user["email"]}: {response.content.decode()}\n'
        assert response.json() == { "email": user["email"], "result": "success" }

"""
Endpoint test: "/user/logout/"

Descripción:
Un usuario puede desloguearse exitosamente.

Escenario exitoso: 200 Ok
Error: 400 Bad Request, 401 Unauthorized, 403 Forbidden

"""
def test_logout_users(users):
    for user in users:
        authorization = USERS_AUTH_DICT[user["email"]][1]

        response = client.post(
            "/user/logout/",
            headers = { "accept": "application/json", "Authorization": authorization }
        )

        assert response.status_code == 200, f'Error {user["email"]}: {response.content.decode()}\n'
