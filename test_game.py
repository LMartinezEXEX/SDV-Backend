from pony.orm import db_session
from fastapi.testclient import TestClient
import json 
import pytest
from datetime import *

from main import app
from Database.database import *


client = TestClient(app)

"""
Creamos un usuario y lo guardamos en la base de datos
"""

with db_session:
    User(
        email="tomasosiecki@gmail.com",
        username="tomuela",
        password="soytomi123",
        icon="hola".encode('utf-8'),
        creation_date=date.today(),
        last_access_date=date.today(),
        is_validated=True,
        active=True
    )

"""
Con los parametros de game_params, el usuario tomasosiecki@gmail.com crea una partida.

Escenario exitoso: 200 Ok
Error: 404 Not Found

"""
game_params = {"email": "tomasosiecki@gmail.com", "name": "Game test", "min_players": 5, "max_players": 5}

def test_create_game(game_params):
    response = client.post(
        "/game/create/",
        headers =  {"accept": "application/json"},
        json = game_params
    )

    assert response.status_code == 201, f'Conflict with {game_params}'
    print(response.status_code)



