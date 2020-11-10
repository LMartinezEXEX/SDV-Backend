import pytest
from main import app
from pony.orm import db_session, select
from datetime import *
from Database.database import *
from fastapi.testclient import TestClient
from pydantic import EmailStr


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
             is_validated=True)

        User(email="aguschapuis@gmail.com",
             username="agus",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True)

        User(email="lautimartinez@gmail.com",
             username="lauti",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True)

        User(email="danireynuaba@gmail.com",
             username="dani",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True)

        User(email="sofigalfre@gmail.com",
             username="sofi",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True)

        User(email="franjoray@gmail.com",
             username="fran",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True)


# Test Functions

def start_new_game(user_email: EmailStr):
    return client.post('game/create/'. format(uu))


def join_a_game(game_id: int, user_email: EmailStr):
     return client.put('game/join/{id}')

def init_the_game(game_id: int, player_id: int):
     return client.put('game/init/{id}')



# TESTS

'''
Test create a game
'''



def test_create_game_with_invalid_email():
     game_params = {"email": 'fake_email@gmail.com', "name": 'Fake Name', "min_players": 5, "max_players": 5}
     response = client.post(
         'game/create/',
         json = game_params
     )

     assert response.status_code == 404
     assert response.json() == {"detail": "User not found"} 


def test_create_game_min_players_less_than_5():
     game_params = {"email": 'tomasosiecki@gmail.com', "name": 'MLBB', "min_players": 3, "max_players": 5}
     response = client.post(
         'game/create/',
         json = game_params
     )

     assert response.status_code == 409
     assert response.json() == {"detail": "The game must have at least 5 players"} 


def test_create_game_max_players_more_than_10():
     game_params = {"email": 'tomasosiecki@gmail.com', "name": 'MLBB', "min_players": 5, "max_players": 11}
     response = client.post(
         'game/create/',
         json = game_params
     )

     assert response.status_code == 409
     assert response.json() == {"detail": "The game must have less than 10 players"} 


def test_incoherent_amount_of_players_to_create_game():
     game_params = {"email": 'tomasosiecki@gmail.com', "name": 'MLBB', "min_players": 10, "max_players": 6}
     response = client.post(
         'game/create/',
         json = game_params
     )

     assert response.status_code == 409
     assert response.json() == {"detail": "The minimum of players is higher than the maximum"} 


def test_create_game_correctly():
     game_params = {"email": 'tomasosiecki@gmail.com', "name": 'MLBB', "min_players": 5, "max_players": 5}
     response = client.post(
         'game/create/',
         json = game_params
     )

     assert response.status_code == 201
     assert response.json() == {"Game_Id": 1, "Player_Id": 1} 


'''
Tests for joining game
'''

def test_join_game_with_invalid_email():
     game_id = 1
     response = client.put(
          'game/join/{}'.format(game_id),
          json= {"email": "fakeemail@gmail.com" })
     
     assert response.status_code == 404
     assert response.json() == {"detail": "User not found"}


def test_join_game_with_invalid_game_id():
     user = {'email': 'tomasosiecki@gmail.com' }
     game_id = 3
     response = client.put(
          'game/join/{}'.format(game_id),
          json=user)
     
     assert response.status_code == 404
     assert response.json() == {"detail": "Game not found"}


def test_join_game():
     user={"email": "aguschapuis@gmail.com"}
     game_id = 1
     response = client.put(
         'game/join/{}'.format(game_id),
         json=user)
     
     assert response.status_code == 200
     assert response.json() == {"Player_Id": 2}


def init_game_bad_game_id():
     game_id = 2
     response = client.put(
          'game/init/{}?player_id=1'.format(game_id))
     
     assert response.status_code == 404
     assert response.json() == {"detail": "Game not found"}


def test_init_game_without_minimum_players():
     game_id = 1
     response = client.put(
          'game/init/{}?player_id=1'.format(game_id))
     
     assert response.status_code == 409
     assert response.json() == {"detail": "The game has not reach the minimum amount of players"}


'''
Test putting three more players in game 1 (with the minimum and maximum of players is 5)
'''
def test_add_players_to_reach_the_min_and_max():
     user1 = {"email": "lautimartinez@gmail.com" }
     user2 = {"email": "danireynuaba@gmail.com"}
     user3 = {"email": "sofigalfre@gmail.com"}
     game_id = 1
     response1 =  client.put(
         'game/join/{}'.format(game_id),
         json=user1)
     response2 =  client.put(
         'game/join/{}'.format(game_id),
         json=user2)
     response3 =  client.put(
         'game/join/{}'.format(game_id),
         json=user3)

     assert response1.status_code == 200
     assert response2.status_code == 200
     assert response3.status_code == 200


def test_join_game_with_maximum_reached():
     user = {"email": "franjoray@gmail.com"}
     game_id = 1
     response = client.put(
         'game/join/{}'.format(game_id),
         json=user)
     
     assert response.status_code == 409
     assert response.json() == {"detail": "The game has reach the maximum amount of players"}


def test_init_game_no_owner():
     game_id = 1
     response = client.put(
          'game/init/{}?player_id=2'.format(game_id))

     assert response.status_code == 409
     assert response.json() == {"detail": "You cant start the game, you are not the owner!"}


def test_init_game():
     game_id = 1
     response = client.put(
          'game/init/{}?player_id=1'.format(game_id))
     
     assert response.status_code == 200



