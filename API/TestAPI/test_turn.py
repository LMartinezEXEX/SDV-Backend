import json
import pytest
from main import app
from pony.orm import db_session, select
from Database.database import *
from fastapi.testclient import TestClient


client = TestClient(app)

# -TEST-CLEARS-THE-DATABASE-BEFORE-STARTING--------------------------------------


@pytest.fixture(scope="session", autouse=True)
def init_data(request):
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    with db_session:

        # Five games instances for test purpose, three 'in game', 1
        # unitiliatlized, 1 finished
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
             creation_date=datetime.datetime.today(),
             state=1)

        Game(name='Forest',
             min_players=4,
             max_players=8,
             creation_date=datetime.datetime.today(),
             state=0)

        Game(name='Habbo',
             min_players=6,
             max_players=6,
             creation_date=datetime.datetime.today(),
             state=2)

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
        game2 = Game[2]

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
        game3 = Game[3]

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
               is_alive=True,
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
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=9,
               rol=1,
               loyalty='Fenix',
               is_alive=True,
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

    request.addfinalizer(clean_db)

# -TEST-CLEARS-DATABASE-AFTER-FINISHING------------------------------------------


def clean_db():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

# -FUNCTIONS-TO-USE-IN-TESTS-----------------------------------------------------


def start_new_turn(game_id):
    return client.put('game/{}/select_MM'.format(game_id))


def start_several_turns(game_id, turns):
    for _ in range(turns):
        client.put('game/{}/select_MM'.format(game_id))


def player_vote(game_id, player_id, vote):
    return client.put('/game/{}/vote'.format(game_id), json={
        "id": player_id,
        "vote": vote
    }
    )


def minister_promulgate(game_id, minister_id, card_type):
    return client.put('/game/{}/promulgate'.format(game_id), json={
        "candidate_id": minister_id,
        "to_promulgate": card_type
    }
    )


def check_game_state(game_id):
    return client.get('game/{}/check_game'.format(game_id))


def get_3_cards(game_id):
    return client.put('/game/{}/get_cards'.format(game_id))

# TESTS--------------------------------------------------------------------------


'''
Test correct response when trying to take action in a game that hasn't started
'''


def test_action_in_uninitialized_game():
    response = start_new_turn(game_id=4)

    assert response.status_code == 409
    assert response.json() == {"detail": "Game hasn't started"}


'''
Test correct response when trying to take action in a finished game
'''


def test_action_in_finished_game():
    response = start_new_turn(game_id=5)

    assert response.status_code == 409
    assert response.json() == {"detail": "Game finished"}


'''
Test correct response when trying to take action in a unexisting game
'''


def test_action_in_unexisting_game():
    response = start_new_turn(game_id=64)

    assert response.status_code == 404
    assert response.json() == {"detail": "Game doesn't exist"}


'''
Test correct response when asked for next minister candidate
'''


def test_candidate_minister():
    response = start_new_turn(game_id=1)

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 1}


'''
Test correct turn assignment in minister candidate position
'''


def test_ciclic_candidate_minister():
    start_several_turns(game_id=1, turns=2)

    response = start_new_turn(game_id=1)

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 1}


'''
Test a dead player can't be selected as minister candidate
'''


def test_candidate_minister_when_dead():
    response = start_new_turn(game_id=2)

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 5}


'''
Test correct turn assignment in minister candidate when dead players are present
'''


def test_ciclic_candidate_minister_when_dead():
    start_several_turns(game_id=2, turns=2)

    response = start_new_turn(game_id=2)

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": 5}


'''
Test correct cards obtained from database
'''


@db_session()
def test_get_cards():
    response = get_3_cards(game_id=1)

    cards = select(c for c in Card if c.game.id == 1).order_by(Card.order)[:]
    cards_type = [cards[0].type, cards[1].type, cards[2].type]

    assert response.status_code == 200
    assert response.json() == {"cards": cards_type}


'''
Test take cards twice in the same turn
'''


@db_session()
def test_get_cards_twice_in_same_turn():
    start_new_turn(game_id=1)

    response = get_3_cards(game_id=1)
    cards = select(
        c for c in Card if c.game.id == 1 and c.order > 3).order_by(
        Card.order)[
            :3]
    cards_type = [cards[0].type, cards[1].type, cards[2].type]

    assert response.status_code == 200
    assert response.json() == {"cards": cards_type}

    response = get_3_cards(game_id=1)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Already taken the cards in this turn"}


'''
Test get cards when a turn hasn't even started in a game
'''


def test_get_cards_with_no_turn():
    response = get_3_cards(game_id=3)

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


'''
Test correct response when a player vote
'''


def test_one_vote_count():
    start_new_turn(game_id=1)

    response = player_vote(game_id=1, player_id=1, vote=True)

    assert response.status_code == 200
    assert response.json() == {"votes": 1}


'''
Test correct response when several player vote
'''


def test_several_vote_count():
    start_new_turn(game_id=2)

    ids = [5, 6]
    votes = [True, False]

    for i in range(2):
        player_vote(game_id=2, player_id=ids[i], vote=votes[i])

    response = player_vote(game_id=2, player_id=7, vote=True)

    assert response.status_code == 200
    assert response.json() == {"votes": 3}


'''
Test a player can't vote in a game it is not in
'''


def test_player_vote_in_invalid_game():
    response = player_vote(game_id=2, player_id=20, vote=True)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not in this game"}


'''
Test candidate promulgate fenix and get right board status
'''


def test_promulgate_fenix():
    start_new_turn(game_id=2)

    response = minister_promulgate(game_id=2, minister_id=7, card_type=0)

    assert response.status_code == 200
    assert response.json() == {
        "fenix promulgations": 1,
        "death eater promulgations": 0}


'''
Test candidate promulgate death eater and get right board status
'''


def test_promulgate_death_eater():
    start_new_turn(game_id=1)

    response = minister_promulgate(game_id=1, minister_id=1, card_type=1)

    assert response.status_code == 200
    assert response.json() == {
        "fenix promulgations": 0,
        "death eater promulgations": 1}


'''
Test a minister can't promulgate twice in the same turn
'''


def test_promulgate_twice():
    start_new_turn(game_id=2)

    minister_promulgate(game_id=2, minister_id=5, card_type=1)

    response = minister_promulgate(game_id=2, minister_id=6, card_type=0)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Minister already promulgated in this turn"}


'''
Test a player that is not the current minister can not promulgate
'''


def test_promulgate_regular_player():
    start_new_turn(game_id=2)

    response = minister_promulgate(game_id=2, minister_id=5, card_type=1)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not minister"}


'''
Test correct game status response
'''


def test_initial_game_check():
    start_new_turn(game_id=3)

    response = check_game_state(game_id=3)

    assert response.status_code == 200
    assert response.json() == {"finished": False,
                               "fenix promulgations": 0,
                               "death eater promulgations": 0,
                               "current minister id": 10,
                               "current director id": 10}


'''
Test correct game status when fenix should win with 5 promulgations
'''


def test_game_check_fenix_five_promulgations():

    minister_ids = [11, 13, 15, 16, 17]
    for i in range(5):
        start_new_turn(game_id=3)
        minister_promulgate(
            game_id=3,
            minister_id=minister_ids[i],
            card_type=0)

    response = check_game_state(game_id=3)

    assert response.status_code == 200
    assert response.json() == {"finished": True,
                               "fenix promulgations": 5,
                               "death eater promulgations": 0,
                               "current minister id": 17,
                               "current director id": 17}


'''
Test correct game status when death eaters should win with 6 promulgations
'''


def test_game_check_six_death_eater_promulgations():

    response = check_game_state(game_id=1)

    assert response.status_code == 200
    assert response.json() == {"finished": False,
                               "fenix promulgations": 0,
                               "death eater promulgations": 1,
                               "current minister id": 1,
                               "current director id": 1}

    minister_ids = [2, 3, 1, 2, 3]
    for i in range(5):
        start_new_turn(game_id=1)
        minister_promulgate(
            game_id=1,
            minister_id=minister_ids[i],
            card_type=1)

    response = check_game_state(game_id=1)

    assert response.status_code == 200
    assert response.json() == {"finished": True,
                               "fenix promulgations": 0,
                               "death eater promulgations": 6,
                               "current minister id": 3,
                               "current director id": 3}
