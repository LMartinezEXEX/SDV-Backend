import pytest
from main import app
from pony.orm import db_session, select
from datetime import *
from Database.database import *
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def init_data(request):
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:

        User(email="tomasosiecki@gmail.com",
             username="tomi",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True,
             refresh_token="HolaKappa",
             refresh_token_expires=datetime.datetime.today())

        User(email="aguschapuis@gmail.com",
             username="agus",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True,
             refresh_token="HolaKappa",
             refresh_token_expires=datetime.datetime.today())

        User(email="lautimartinez@gmail.com",
             username="lauti",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True,
             refresh_token="HolaKappa",
             refresh_token_expires=datetime.datetime.today())

        User(email="danireynuaba@gmail.com",
             username="dani",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True,
             refresh_token="HolaKappa",
             refresh_token_expires=datetime.datetime.today())

        User(email="sofigalfre@gmail.com",
             username="sofi",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True,
             refresh_token="HolaKappa",
             refresh_token_expires=datetime.datetime.today())

        User(email="franjoray@gmail.com",
             username="fran",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True,
             refresh_token="HolaKappa",
             refresh_token_expires=datetime.datetime.today())


# Test Functions

def start_new_game(user_email: email):
    return client.post('game/create')






# TESTS

'''
Test create a game
'''

def test_create_game():
    response = 
