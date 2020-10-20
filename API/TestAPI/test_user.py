# Default Responses for the API for testing purposes
from fastapi.testclient import TestClient
import json

from main import app

client = TestClient(app)

USERS = [
    {
        "email": "superman@justiceleague.com",
        "username": "Clark Kent",
        "password": "kkkkk12323",
    },
    {
        "email": "batman@justiceleague.com",
        "username": "Bruno Diaz",
        "password": "kadssdkkkk",
    },
    {
        "email": "robin@justiceleague.com",
        "username": "RicardoTapia",
        "password": "987979oo68i7",
    },
    {
        "email": "wonderwoman@justiceleague.com",
        "username": "DianaPrince",        
        "password": "421413434234",
    },
    {
        "email": "thor@gmail.com",
        "username": "nothor22",
        "password": "kkkasdskk"
    },
    {
        "email": "thejoker@gmail.com",
        "username": "thejoker",
        "password": "kkkasdskk"
    },

]

"""
Tiene que funcionar la primera vez que lo ejecutan, la segunda no porque el endpoint tira error si
alguien intenta registrar un usuario que ya esta
"""
def test_register_users():
    for user in USERS:
        user_register = { "email": user["email"], "username": user["username"], "password": user["password"] }
        response = client.post(
            "/user/register/",
            headers = { "accept": "application/json" },
            json    = user_register
        )
        
        assert response.status_code == 201

