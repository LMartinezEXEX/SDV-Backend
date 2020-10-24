import json
import pytest
from main import app
from pony.orm import db_session, select
from Database.database import *
from fastapi.testclient import TestClient


client = TestClient(app)

'''
Tests need to be executed with an empty database!
'''

#TEST-DATA----------------------------------------------------------------------
with db_session:

# Three games instances for test purpose
    Game(name='LOL',
          min_players=5,
          max_players=5,
          creation_date=datetime.datetime.today(),
          state=1)

    Game(name='WOW',
        min_players=5,
        max_players=10,
        creation_date=datetime.datetime.today(),
        state=1)

    Game(name='Among Us',
        min_players=6,
        max_players=8,
        creation_date = datetime.datetime.today(),
        state=1)



# Three players in LOL alives
    game1 = Game[1]

    Player(turn=1,
            rol=1,
            loyalty='Fenix',
            is_alive=True,
            chat_enabled=True,
            is_investigated=False,
            game_in=game1.id)

    Player(turn=2,
            rol=1,
            loyalty='Fenix',
            is_alive=True,
            chat_enabled=True,
            is_investigated=False,
            game_in=game1.id)

    Player(turn=3,
            rol=2,
            loyalty='Mortifago',
            is_alive=True,
            chat_enabled=True,
            is_investigated=False,
            game_in=game1.id)

# Five players in WOW, two of them dead
    game2=Game[2]

    Player(turn=1,
            rol=1,
            loyalty='Fenix',
            is_alive=False,
            chat_enabled=True,
            is_investigated=False,
            game_in=game2.id)

    Player(turn=2,
            rol=1,
            loyalty='Fenix',
            is_alive=True,
            chat_enabled=True,
            is_investigated=False,
            game_in=game2.id)

    Player(turn=3,
            rol=2,
            loyalty='Mortifago',
            is_alive=True,
            chat_enabled=True,
            is_investigated=False,
            game_in=game2.id)

    Player(turn=4,
            rol=1,
            loyalty='Fenix',
            is_alive=True,
            chat_enabled=True,
            is_investigated=False,
            game_in=game2.id)

    Player(turn=5,
            rol=2,
            loyalty='Mortifago',
            is_alive=False,
            chat_enabled=True,
            is_investigated=False,
            game_in=game2.id)

# Ten players in Among Us, three of them dead
    game3=Game[3]

    Player(turn=1,
            rol=1,
            loyalty='Fenix',
            is_alive=False,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

    Player(turn=2,
            rol=1,
            loyalty='Fenix',
            is_alive=True,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

    Player(turn=3,
            rol=2,
            loyalty='Mortifago',
            is_alive=True,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

    Player(turn=4,
            rol=1,
            loyalty='Fenix',
            is_alive=False,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

    Player(turn=5,
            rol=2,
            loyalty='Mortifago',
            is_alive=False,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

    Player(turn=6,
            rol=1,
            loyalty='Fenix',
            is_alive=False,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

    Player(turn=7,
            rol=1,
            loyalty='Fenix',
            is_alive=True,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

    Player(turn=8,
            rol=2,
            loyalty='Mortifago',
            is_alive=False,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

    Player(turn=9,
            rol=1,
            loyalty='Fenix',
            is_alive=False,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

    Player(turn=10,
            rol=2,
            loyalty='Mortifago',
            is_alive=False,
            chat_enabled=True,
            is_investigated=False,
            game_in=game3.id)

#TESTS--------------------------------------------------------------------------

'''
Test correct response when asked for next minister candidate
'''
def test_candidate_minister():
    response = client.put("/game/1/select_MM")

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 1}


'''
Test correct turn assignment in minister candidate position
'''
def test_ciclic_candidate_minister():
    response = client.put("/game/1/select_MM")

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 2}

    response = client.put("/game/1/select_MM")

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 3}

    response = client.put("/game/1/select_MM")

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 1}


'''
Test a dead player can't be selected as minister candidate
'''
def test_candidate_minister_when_dead():
    response = client.put("/game/2/select_MM")

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 5}


'''
Test correct turn assignment in minister candidate when dead players are present
'''
def test_ciclic_candidate_minister_when_dead():
    response = client.put("/game/2/select_MM")

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 6}

    response = client.put("/game/2/select_MM")

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 7}

    response = client.put("/game/2/select_MM")

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 5}


'''
Test correct cards obtained from database
'''
@db_session()
def test_get_cards():
    response = client.put("/game/1/get_cards")

    cards = select(c for c in Card if c.game.id==1).order_by(Card.order)[:]
    cards_type = [cards[0].type, cards[1].type, cards[2].type]

    assert response.status_code == 200
    assert response.json() == {"cards": cards_type}


'''
Test take cards twice in the same turn
'''
@db_session()
def test_get_cards_twice_in_same_turn():
    client.put("/game/1/select_MM")

    response = client.put("/game/1/get_cards")
    cards = select(c for c in Card if c.game.id==1 and c.order > 3).order_by(Card.order)[:3]
    cards_type = [cards[0].type, cards[1].type, cards[2].type]

    assert response.status_code == 200
    assert response.json() == {"cards": cards_type}

    response = client.put("/game/1/get_cards")

    assert response.status_code == 400


'''
Test get cards when a turn hasn't even started in a game
'''
def test_get_cards_with_no_turn():
    response = client.put("/game/3/get_cards")

    assert response.status_code == 409


'''
Test correct response when a player vote
'''
def test_one_vote_count():
    client.put("/game/1/select_MM")

    response = client.put("/game/1/vote",
                            json={
                                "id": 1,
                                "vote": True
                            }
                         )

    assert response.status_code == 200
    assert response.json() == {"votes": 1}


'''
Test correct response when several player vote
'''
def test_several_vote_count():
    client.put("/game/2/select_MM")

    client.put("/game/2/vote", json={
                                "id": 5,
                                "vote": True
                                    }
              )

    client.put("/game/2/vote", json={
                                "id": 6,
                                "vote": False
                                    }
              )

    response = client.put("/game/2/vote", json={
                                "id": 7,
                                "vote": True
                                    }
                         )

    assert response.status_code == 200
    assert response.json() == {"votes": 3}


'''
Test a player can't vote in a game it is not in
'''
def test_player_vote_in_invalid_game():
    response = client.put("/game/2/vote", json={
                                "id": 20,
                                "vote": True
                                    }
                         )

    assert response.status_code == 400
