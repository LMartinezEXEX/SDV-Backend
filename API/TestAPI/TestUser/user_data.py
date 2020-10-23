import pytest

UPDATE_USERNAME_STRING = "update_username"

UPDATE_PASSWORD_STRING = "update_pass"



""" Necesito compartir usuarios para las pruebas.
"""
@pytest.fixture
def users():
    return [
    {
        "email": "superman@justiceleague.com",
        "username": "ClarkKent",
        "password": "12345678",
    },
    {
        "email": "batman@justiceleague.com",
        "username": "BrunoDiaz",
        "password": "12345678",
    },
    {
        "email": "robin@justiceleague.com",
        "username": "RicardoTapia",
        "password": "12345678",
    },
    {
        "email": "wonderwoman@justiceleague.com",
        "username": "DianaPrince",        
        "password": "12345678",
    },
    {
        "email": "thor@gmail.com",
        "username": "thethor22",
        "password": "12345678"
    },
    {
        "email": "thejoker@gmail.com",
        "username": "thejoker",
        "password": "12345678"
    },

]