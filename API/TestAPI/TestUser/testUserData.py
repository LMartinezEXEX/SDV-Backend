import pytest

UPDATE_USERNAME_STRING = "update_username"

UPDATE_PASSWORD_STRING = "update_pass"

UPDATE_XML_DIR  = "img"
UPDATE_XML_FILE = "note.xml"

UPDATE_HTML_DIR  = "img"
UPDATE_HTML_FILE = "note.html"

UPDATE_ICON_DIR  = "img"
UPDATE_ICON_FILE = "grumpycat.jpeg"

""" Necesito compartir usuarios para las pruebas.
"""
USERS = [
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

@pytest.fixture
def users():
    return USERS