import json
import pytest
from main import app
from pony.orm import db_session, select
from Database.database import *
from fastapi.testclient import TestClient


client = TestClient(app)


# -SET-UP-----------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def init_data(request):
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    request.addfinalizer(clean_db)

# -TEAR-DOWN--------------------------------------------------------------------


def clean_db():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()


total_players = 0
games = 0


@db_session()
def game_factory(players_cuantity: int, turns_cuantity: int,
                 game_state: int = 1, dead_player: bool = False, dead_cuantity: int = 0):
    global total_players
    global games

    users = []
    # Create users
    for user in range(players_cuantity):
        user = User(email='usuario{}@gmail.br'.format(total_players),
                    username='User_{}'.format(total_players),
                    password="fachero".encode(),
                    icon="".encode(),
                    creation_date=datetime.datetime.today(),
                    last_access_date=datetime.datetime.today(),
                    is_validated=True,
                    refresh_token="HolaKappa",
                    refresh_token_expires=datetime.datetime.today())
        users.append(user)
        total_players += 1

    owner = User['usuario{}@gmail.br'.format(total_players - players_cuantity)]

    # Create game and Board
    game = Game(name='test_game_{}'.format(games),
                owner=owner,
                min_players=5,
                max_players=10,
                creation_date=datetime.datetime.today(),
                state=game_state)
    games += 1

    Board(game=game,
          fenix_promulgation=0,
          death_eater_promulgation=0,
          election_counter=0)
    commit()

    game_id = game.id

    players = []
    turn = 1
    # Join players in game
    for user in users:
        player = Player(turn=turn,
                        user=user,
                        rol='Fenix',
                        loyalty='Fenix',
                        is_alive=True,
                        chat_enabled=True,
                        is_investigated=False,
                        game_in=game)
        players.append(player)
        turn += 1

    # Kill first 'dead_cuantity' players
    if dead_player:
        player_index = 0
        for _ in range(dead_cuantity):
            player = players[player_index]
            player.is_alive = False
            player_index += 1
    commit()

    for _ in range(turns_cuantity):
        response = client.put('game/{}/select_MM'.format(game_id))

    return [game_id, players[0].id]


def make_vote_and_start_new_turn(
        game_id: int, players_to_vote: int, first_player_id: int, result: bool, dead_count: int = 0):
    # Vote the formula
    for i in range(players_to_vote):
        player_vote(
            game_id=game_id,
            player_id=first_player_id + dead_count + i,
            vote=result)

    client.put('game/{}/result'.format(game_id))

    # Now minister id is game_data[1]+4
    start_new_turn(game_id)


def start_new_turn(game_id):
    return client.put('game/{}/select_MM'.format(game_id))


def get_3_cards(game_id):
    return client.put('/game/{}/get_cards'.format(game_id))


def check_game_state(game_id):
    return client.get('game/{}/check_game'.format(game_id))


def get_director_candidates(game_id):
    return client.get('/game/{}/director_candidates'.format(game_id))


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


def set_director_candidate(game_id, minister_id, director_id):
    return client.put('/game/{}/select_director_candidate'.format(game_id), json={
        "minister_id": minister_id,
        "director_id": director_id
    }
    )

# -TESTS------------------------------------------------------------------------


'''
Test correct response when trying to take action in a game that hasn't started
'''


def test_action_in_uninitialized_game():
    game_data = game_factory(5, 1, 0)
    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 409
    assert response.json() == {"detail": "Game hasn't started"}


'''
Test correct response when trying to take action in a finished game
'''


def test_action_in_finished_game():
    game_data = game_factory(5, 1, 2)
    response = start_new_turn(game_id=game_data[0])

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
    game_data = game_factory(5, 0)
    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1]}


'''
Test correct turn assignment in minister candidate position
'''


def test_ciclic_candidate_minister():
    game_data = game_factory(5, 3)

    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1] + 3}


'''
Test a dead player can't be selected as minister candidate
'''


def test_candidate_minister_when_dead():
    game_data = game_factory(5, 0, 1, True, 1)
    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1] + 1}


'''
Test correct turn assignment in minister candidate when dead players are present
'''


def test_ciclic_candidate_minister_when_dead():
    game_data = game_factory(5, 12, 1, True, 2)
    response = start_new_turn(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"candidate_minister_id": game_data[1] + 2}


'''
Test correct cards obtained from database
'''


@db_session()
def test_get_cards():
    game_data = game_factory(7, 12)
    response = get_3_cards(game_id=game_data[0])

    cards = select(
        c for c in Card if c.game.id == game_data[0]).order_by(
        Card.order)[:]
    cards_type = [cards[0].type, cards[1].type, cards[2].type]

    assert response.status_code == 200
    assert response.json() == {"cards": cards_type}


'''
Test take cards twice in the same turn
'''


@db_session()
def test_get_cards_twice_in_same_turn():
    game_data = game_factory(5, 6)
    get_3_cards(game_id=game_data[0])

    response = get_3_cards(game_id=game_data[0])

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Already taken the cards in this turn"}


'''
Test get cards when a turn hasn't even started in a game
'''


def test_get_cards_with_no_turn():
    game_data = game_factory(7, 0)
    response = get_3_cards(game_id=game_data[0])

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


'''
Test correct response when a player vote
'''


def test_one_vote_count():
    game_data = game_factory(7, 1)
    response = player_vote(
        game_id=game_data[0],
        player_id=game_data[1],
        vote=True)

    assert response.status_code == 200
    assert response.json() == {"votes": 1}


'''
Test correct response when several player vote
'''


def test_several_vote_count():
    game_data = game_factory(5, 1)
    response = None

    votes = [True, False, True, True, False]
    for i in range(5):
        response = player_vote(
            game_id=game_data[0],
            player_id=game_data[1] + i,
            vote=votes[i])

    assert response.status_code == 200
    assert response.json() == {"votes": 5}


'''
Test a player cant vote when the game has no turn started
'''


def test_vote_with_no_turn_in_game():
    game_data = game_factory(5, 0)
    response = player_vote(
        game_id=game_data[0],
        player_id=game_data[1],
        vote=True)

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


'''
Test a player can't vote in a game it is not in
'''


def test_player_vote_in_game_its_not_in():
    game_data = game_factory(7, 5)
    response = player_vote(
        game_id=game_data[0],
        player_id=game_data[1] + 40,
        vote=True)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not in this game"}


'''
Assert all players voted before giving the final result
'''


def test_get_result_when_votes_missing():
    game_data = game_factory(5, 1)
    response = client.put('game/{}/result'.format(game_data[0]))

    assert response.status_code == 409
    assert response.json() == {"detail": "Vote's missing"}


'''
Test correct response when trying to get a vote result when the gama has
no turn started and therefore a vote session
'''


def test_get_result_when_no_turn():
    game_data = game_factory(10, 0)
    response = client.put('game/{}/result'.format(game_data[0]))

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


'''
Test correct result when all players voted
'''


def test_get_result():
    game_data = game_factory(7, 1)

    votes = [True, True, False, True, True, False, False]
    voted_lumos = [
        game_data[1],
        game_data[1] + 1,
        game_data[1] + 3,
        game_data[1] + 4]

    for i in range(7):
        player_vote(
            game_id=game_data[0],
            player_id=game_data[1] + i,
            vote=votes[i])

    response = client.put('game/{}/result'.format(game_data[0]))

    assert response.status_code == 200
    assert response.json() == {"result": True, "voted_lumos": voted_lumos}


'''
Test correct response when trying to promulgate when the gama has
no turn started and therefore no legislative session
'''


def test_promulgate_with_no_turn():
    game_data = game_factory(7, 0)
    response = minister_promulgate(
        game_id=game_data[0],
        minister_id=game_data[1],
        card_type=0)

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


'''
Test candidate promulgate fenix and get right board status
'''


def test_promulgate_fenix():
    game_data = game_factory(7, 1)

    response = minister_promulgate(
        game_id=game_data[0],
        minister_id=game_data[1],
        card_type=0)

    assert response.status_code == 200
    assert response.json() == {
        "fenix promulgations": 1,
        "death eater promulgations": 0}


'''
Test candidate promulgate death eater and get right board status
'''


def test_promulgate_death_eater():
    game_data = game_factory(7, 1)

    response = minister_promulgate(
        game_id=game_data[0],
        minister_id=game_data[1],
        card_type=1)

    assert response.status_code == 200
    assert response.json() == {
        "fenix promulgations": 0,
        "death eater promulgations": 1}


'''
Test a minister can't promulgate twice in the same turn
'''


def test_promulgate_twice():
    game_data = game_factory(7, 1)

    minister_promulgate(
        game_id=game_data[0],
        minister_id=game_data[1],
        card_type=1)

    response = minister_promulgate(
        game_id=game_data[0],
        minister_id=game_data[1],
        card_type=0)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Minister already promulgated in this turn"}


'''
Test a player that is not the current minister can not promulgate
'''


def test_promulgate_regular_player():
    game_data = game_factory(10, 3)

    response = minister_promulgate(
        game_id=game_data[0],
        minister_id=game_data[0],
        card_type=1)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not minister"}


'''
Test correct response when getting the initial game state without turn started
'''


def test_game_check_with_no_turn():
    game_data = game_factory(10, 0)
    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": False,
                               "fenix promulgations": 0,
                               "death eater promulgations": 0,
                               "current minister id": None,
                               "current director id": None}


'''
Test correct game status response
'''


def test_initial_game_check():
    game_data = game_factory(8, 1)

    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": False,
                               "fenix promulgations": 0,
                               "death eater promulgations": 0,
                               "current minister id": game_data[1],
                               "current director id": game_data[1]}


'''
Test correct game status when fenix should win with 5 promulgations
'''


def test_game_check_fenix_five_promulgations():
    game_data = game_factory(8, 0, 1, True, 3)

    for i in range(5):
        start_new_turn(game_id=game_data[0])
        response = minister_promulgate(
            game_id=game_data[0],
            minister_id=game_data[1] + i + 3,
            card_type=0)

    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": True,
                               "fenix promulgations": 5,
                               "death eater promulgations": 0,
                               "current minister id": game_data[1] + 7,
                               "current director id": game_data[1] + 7}


'''
Test correct game status when death eaters should win with 6 promulgations
'''


def test_game_check_six_death_eater_promulgations():
    game_data = game_factory(10, 0, 1, True, 2)

    for i in range(6):
        start_new_turn(game_id=game_data[0])
        minister_promulgate(
            game_id=game_data[0],
            minister_id=game_data[1] + i + 2,
            card_type=1)

    response = check_game_state(game_id=game_data[0])

    assert response.status_code == 200
    assert response.json() == {"game id": game_data[0],
                               "finished": True,
                               "fenix promulgations": 0,
                               "death eater promulgations": 6,
                               "current minister id": game_data[1] + 7,
                               "current director id": game_data[1] + 7}


'''
Test endpoint returns all ids (except candidate for minister) when asking
for director candidate ids, because theres no restriction with preivous
selected formula
'''


def test_get_director_candidate_ids_with_no_restriction():
    game_data = game_factory(10, 1)

    response = get_director_candidates(game_data[0])

    candidates = []

    for i in range(9):
        candidates.append(game_data[1] + 1 + i)

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}


'''
Assert correst response when trying ro get director candidates with
no turn, (i.e. candidate minister) yet.
'''


def test_get_director_candidate_ids_with_no_turn():
    game_data = game_factory(10, 0)

    response = get_director_candidates(game_data[0])

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


'''
Test correct response when there's a restriction because of a previous
accepted formula in the game
'''


def test_get_director_candidates_ids_with_minister_restriction():
    game_data = game_factory(7, 2)

    make_vote_and_start_new_turn(game_data[0], 7, game_data[1], True)

    candidates = [
        game_data[1],
        game_data[1] + 3,
        game_data[1] + 4,
        game_data[1] + 5,
        game_data[1] + 6]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}


'''
Assert correct response, we know the valid director candidate ids; it should be
retrived by the endpoint in the real game
'''


def test_set_director_candidate():
    game_data = game_factory(10, 1)

    response = set_director_candidate(
        game_data[0], game_data[1], game_data[1] + 7)

    assert response.status_code == 200
    assert response.json() == {
        "candidate minister id": game_data[1],
        "candidate director id": game_data[1] + 7}


'''
Assert that is not possible set director with no turn started
'''


def test_set_director_with_no_turn():
    game_data = game_factory(10, 0)

    response = set_director_candidate(
        game_data[0], game_data[1], game_data[1] + 7)

    assert response.status_code == 409
    assert response.json() == {"detail": "No turn started yet"}


'''
Test correct response when the player who sets the director candidate isn't
the current minister in the current turn
'''


def test_set_director_with_incorret_minister_id():
    game_data = game_factory(10, 1)

    response = set_director_candidate(
        game_data[0], game_data[1] + 20, game_data[1] + 7)

    assert response.status_code == 409
    assert response.json() == {"detail": "Player is not minister"}


'''
Assert correct response when trying to set twice director candidate, regardless
of the id
'''


def test_set_director_twice():
    game_data = game_factory(10, 3)

    set_director_candidate(game_data[0], game_data[1] + 2, game_data[1] + 7)

    response = set_director_candidate(
        game_data[0], game_data[1] + 2, game_data[1] + 10)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Already set director candidate in current turn"}


'''
This test simulates a legislative session (without cards work), to assert
the correct director candidates in different turns
'''


def test_get_director_candidate_after_multiple_selected_director():
    game_data = game_factory(7, 3)

    set_director_candidate(game_data[0], game_data[1] + 2, game_data[1])

    make_vote_and_start_new_turn(game_data[0], 7, game_data[1], True)

    candidates = [
        game_data[1] + 1,
        game_data[1] + 4,
        game_data[1] + 5,
        game_data[1] + 6]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}

    set_director_candidate(game_data[0], game_data[1] + 3, game_data[1] + 1)

    make_vote_and_start_new_turn(game_data[0], 7, game_data[1], True)

    candidates = [
        game_data[1],
        game_data[1] + 2,
        game_data[1] + 5,
        game_data[1] + 6]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}

    set_director_candidate(game_data[0], game_data[1] + 4, game_data[1] + 6)

    make_vote_and_start_new_turn(game_data[0], 7, game_data[1], False)

    candidates = [
        game_data[1],
        game_data[1] + 2,
        game_data[1] + 4,
        game_data[1] + 6]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}


'''
This test simulates a legislative session (without cards work) with five
alive player to test this elegibility condition in the game
'''


def test_get_director_candidate_ids_with_five_player_restriction():
    game_data = game_factory(5, 1)

    set_director_candidate(game_data[0], game_data[1], game_data[1] + 3)

    make_vote_and_start_new_turn(game_data[0], 5, game_data[1], True)

    candidates = [game_data[1],
                  game_data[1] + 2,
                  game_data[1] + 4]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}

    set_director_candidate(game_data[0], game_data[1] + 1, game_data[1] + 2)

    make_vote_and_start_new_turn(game_data[0], 5, game_data[1], False)

    candidates = [game_data[1],
                  game_data[1] + 1,
                  game_data[1] + 4]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}

    set_director_candidate(game_data[0], game_data[1] + 2, game_data[1])

    make_vote_and_start_new_turn(game_data[0], 5, game_data[1], False)

    candidates = [
        game_data[1],
        game_data[1] + 1,
        game_data[1] + 2,
        game_data[1] + 4]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}


'''
Test director candidates elegibility with 5 alive player between 7 players
'''


def test_get_director_candidate_ids_with_five_player_dead_players():
    game_data = game_factory(7, 1, 1, True, 2)

    set_director_candidate(game_data[0], game_data[1] + 2, game_data[1] + 4)

    make_vote_and_start_new_turn(game_data[0], 5, game_data[1], True, 2)

    candidates = [game_data[1] + 2,
                  game_data[1] + 5,
                  game_data[1] + 6]

    response = get_director_candidates(game_data[0])

    assert response.status_code == 200
    assert response.json() == {"director candidates": candidates}
