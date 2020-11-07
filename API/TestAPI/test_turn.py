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

        User(email="lautaro@gmail.br",
             username="pepo",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True,
             refresh_token="HolaKappa",
             refresh_token_expires=datetime.datetime.today())

        user = User["lautaro@gmail.br"]

        # Five games instances for test purpose, three 'in game', 1
        # unitiliatlized, 1 finished
        Game(name='LOL',
             owner=user,
             min_players=5,
             max_players=5,
             creation_date=datetime.datetime.today(),
             state=1)

        Game(name='WOW',
             owner=user,
             min_players=5,
             max_players=10,
             creation_date=datetime.datetime.today(),
             state=1)

        Game(name='Among Us',
             owner=user,
             min_players=6,
             max_players=8,
             creation_date=datetime.datetime.today(),
             state=1)

        Game(name='Pokemon',
             owner=user,
             min_players=7,
             max_players=8,
             creation_date=datetime.datetime.today(),
             state=1)

        Game(name='Kirby',
             owner=user,
             min_players=5,
             max_players=6,
             creation_date=datetime.datetime.today(),
             state=1)

        Game(name='Sonic',
             owner=user,
             min_players=9,
             max_players=10,
             creation_date=datetime.datetime.today(),
             state=1)

        Game(name='Mario Bros',
             owner=user,
             min_players=9,
             max_players=10,
             creation_date=datetime.datetime.today(),
             state=1)

        Game(name='Forest',
             owner=user,
             min_players=4,
             max_players=8,
             creation_date=datetime.datetime.today(),
             state=0)

        Game(name='Habbo',
             owner=user,
             min_players=6,
             max_players=6,
             creation_date=datetime.datetime.today(),
             state=2)

        # Three players in LOL alives
        game1 = Game[1]

        Board(game=game1,
              fenix_promulgation=0,
              death_eater_promulgation=0,
              election_counter=0)

        Player(turn=1,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game1.id)

        Player(turn=2,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game1.id)

        Player(turn=3,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game1.id)

        # Five players in WOW, two of them dead
        game2 = Game[2]

        Board(game=game2,
              fenix_promulgation=0,
              death_eater_promulgation=0,
              election_counter=0)

        Player(turn=1,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=False,
               chat_enabled=True,
               is_investigated=False,
               game_in=game2.id)

        Player(turn=2,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game2.id)

        Player(turn=3,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game2.id)

        Player(turn=4,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game2.id)

        Player(turn=5,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=False,
               chat_enabled=True,
               is_investigated=False,
               game_in=game2.id)

        # Ten players in Among Us, three of them dead
        game3 = Game[3]

        Board(game=game3,
              fenix_promulgation=0,
              death_eater_promulgation=0,
              election_counter=0)

        Player(turn=1,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=False,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=2,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=3,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=4,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=False,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=5,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=6,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=False,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=7,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=8,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=9,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        Player(turn=10,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=False,
               chat_enabled=True,
               is_investigated=False,
               game_in=game3.id)

        game4 = Game[4]
        Board(game=game4,
              fenix_promulgation=0,
              death_eater_promulgation=1,
              election_counter=0)

        Player(turn=1,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game4.id)

        Player(turn=2,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game4.id)

        Player(turn=3,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game4.id)

        Player(turn=4,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game4.id)

        Player(turn=5,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game4.id)

        Player(turn=6,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game4.id)

        Player(turn=7,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game4.id)

        game5 = Game[5]
        Board(game=game5,
              fenix_promulgation=0,
              death_eater_promulgation=2,
              election_counter=0)

        Player(turn=1,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game5.id)

        Player(turn=2,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game5.id)

        Player(turn=3,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game5.id)

        Player(turn=4,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game5.id)

        Player(turn=5,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game5.id)

        game6 = Game[6]
        Board(game=game6,
              fenix_promulgation=0,
              death_eater_promulgation=0,
              election_counter=0)

        Player(turn=1,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        Player(turn=2,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        Player(turn=3,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        Player(turn=4,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        Player(turn=5,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        Player(turn=6,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        Player(turn=7,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        Player(turn=8,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        Player(turn=9,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        Player(turn=10,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game6.id)

        game7 = Game[7]
        Board(game=game7,
              fenix_promulgation=0,
              death_eater_promulgation=2,
              election_counter=0)

        Player(turn=1,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game7.id)

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


def get_spells_in_new_turn(game_id, minister_id, card_type):
    start_new_turn(game_id)
    minister_promulgate(game_id, minister_id, card_type)

    return client.get('/game/{}/spell'.format(game_id))


def check_game_state(game_id):
    return client.get('game/{}/check_game'.format(game_id))


def get_3_cards(game_id):
    return client.put('/game/{}/get_cards'.format(game_id))

# TESTS--------------------------------------------------------------------------


'''
Test correct response when trying to take action in a game that hasn't started
'''


def test_action_in_uninitialized_game():
    response = start_new_turn(game_id=8)

    assert response.status_code == 409
    assert response.json() == {"detail": "Game hasn't started"}


'''
Test correct response when trying to take action in a finished game
'''


def test_action_in_finished_game():
    response = start_new_turn(game_id=9)

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
Test a player cant vote when the game just started and no turn is given yet
'''


def test_vote_with_no_turn_in_game():
    response = player_vote(game_id=3, player_id=7, vote=True)

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


'''
Test a player can't vote in a game it is not in
'''


def test_player_vote_in_invalid_game():
    response = player_vote(game_id=2, player_id=20, vote=True)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not in this game"}


'''
Assert all players voted before giving the final result
'''


def test_get_result_when_votes_missing():
    response = client.put("game/1/result")

    assert response.status_code == 409
    assert response.json() == {"detail": "Vote's missing"}


'''
Test correct response when trying to get a vote result when the gama has
no turn started and therefore a vote session
'''


def test_get_result_when_no_turn():
    response = client.put("game/3/result")

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


'''
Test correct result when all players voted
'''


def test_get_result():
    player_vote(game_id=1, player_id=2, vote=True)
    player_vote(game_id=1, player_id=3, vote=False)

    response = client.put("game/1/result")

    assert response.status_code == 200
    assert response.json() == {"result": True, "voted_lumos": [1, 2]}


'''
Test correct response when trying to promulgate when the gama has
no turn started and therefore no legislative session
'''


def test_promulgate_with_no_turn():
    response = minister_promulgate(game_id=3, minister_id=10, card_type=0)

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


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
Test correct response when getting the initial game state without turn started
'''


def test_game_ckeck_with_no_turn():
    response = check_game_state(game_id=3)

    assert response.status_code == 200
    assert response.json() == {"game id": 3,
                               "finished": False,
                               "fenix promulgations": 0,
                               "death eater promulgations": 0,
                               "current minister id": None,
                               "current director id": None}


'''
Test correct game status response
'''


def test_initial_game_check():
    start_new_turn(game_id=3)

    response = check_game_state(game_id=3)

    assert response.status_code == 200
    assert response.json() == {"game id": 3,
                               "finished": False,
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
    assert response.json() == {"game id": 3,
                               "finished": True,
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
    assert response.json() == {"game id": 1,
                               "finished": False,
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
    assert response.json() == {"game id": 1,
                               "finished": True,
                               "fenix promulgations": 0,
                               "death eater promulgations": 6,
                               "current minister id": 3,
                               "current director id": 3}


'''
Test correct response with no available spells in a game with no turn
'''


def test_available_spell_with_no_turn():
    response = client.get("/game/4/spell")

    assert response.status_code == 200
    assert response.json() == {"Spell": ""}


def test_available_spells_board_with_invalid_players_count():
    response = get_spells_in_new_turn(game_id=7, minister_id=41, card_type=1)

    assert response.status_code == 200
    assert response.json() == {"Spell": ""}


'''
Test correct spells in board with 5 to 6 players
'''


def test_available_spells_board_1():
    start_new_turn(game_id=5)

    response = client.get("/game/5/spell")

    assert response.status_code == 200
    assert response.json() == {"Spell": ""}

    minister_promulgate(game_id=5, minister_id=26, card_type=1)

    response = client.get("/game/5/spell")

    assert response.status_code == 200
    assert response.json() == {"Spell": "Guessing"}

    for i in range(2):
        response = get_spells_in_new_turn(
            game_id=5, minister_id=27 + i, card_type=1)

        assert response.status_code == 200
        assert response.json() == {"Spell": "Avada Kedavra"}


'''
Test correct spells in board with 7 to 8 players
'''


def test_available_spells_board_2():
    start_new_turn(game_id=4)

    response = client.get("/game/4/spell")

    assert response.status_code == 200
    assert response.json() == {"Spell": ""}

    minister_promulgate(game_id=4, minister_id=19, card_type=1)

    response = client.get("/game/4/spell")

    assert response.status_code == 200
    assert response.json() == {"Spell": "Crucio"}

    spells = ["Imperius", "Avada Kedavra", "Avada Kedavra"]
    for i in range(3):
        response = get_spells_in_new_turn(
            game_id=4, minister_id=20 + i, card_type=1)

        assert response.status_code == 200
        assert response.json() == {"Spell": spells[i]}


'''
Test correct spells in board with 9 to 10 players
'''


def test_available_spells_board_3():
    start_new_turn(game_id=6)

    response = client.get("/game/6/spell")

    assert response.status_code == 200
    assert response.json() == {"Spell": ""}

    minister_promulgate(game_id=6, minister_id=31, card_type=1)

    response = client.get("/game/6/spell")

    assert response.status_code == 200
    assert response.json() == {"Spell": "Crucio"}

    spells = ["Crucio", "Imperius", "Avada Kedavra", "Avada Kedavra"]
    for i in range(4):
        response = get_spells_in_new_turn(
            game_id=6, minister_id=32 + i, card_type=1)

        assert response.status_code == 200
        assert response.json() == {"Spell": spells[i]}
