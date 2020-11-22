import json
import pytest
import datetime
from main import app
from pony.orm import db_session, select
from Database.database import *
from fastapi.testclient import TestClient
from API.Model.userAPI import *
from API.Model.gameAPI import *
from API.Model.turnAPI import *
from API.Model.voteAPI import *
from API.Model.cardAPI import *
from API.Model.playerAPI import *
from API.Model.spellAPI import *
from API.Model.boardAPI import *
from API.Model.exceptions import *
from API.Model.metadata import *
from API.Model.models import DiscardData, EmailParameter


client = TestClient(app)

'''
Global values to keep track cuantity of games and players in DB
'''
total_players = 0
games = 0


'''
Game factory creates a new game with entablished conditions:

* [Required] players cuantity: int
* [Required] turns cuantity: int = note that if the state parameter is True, there
would be one turn started because the game initiation.
* start: bool = If game should be initialized (always with the init game endpoint)
* game_state: int = 1 for uninitialized game state
                    2 for initialized game state (therefore game will start
                    without a first turn and cant be able to call init game endpoint)
                    3 for finished game state

* dead_player: bool = If should be dead players in the game.
* dead_cuantity: int = amount of first players that should be dead, dead_player
must be True
* fenix_promulgation: int
* death_eater_promulgation: int

Return:

* [game_id: int, first_player_id: int] = where:
    * game_id is the id of the game created.
    * first_player_id is the id of the first player in the game.

Note:
1) All players with even turn number would be Fenix.
2) Last player in game would de Voldemort.
'''
@db_session()
def game_factory(players_cuantity: int, turns_cuantity: int, start: bool = True,
                 game_state: int = 1, dead_player: bool = False, dead_cuantity: int = 0,
                 fenix_promulgation: int = 0, death_eater_promulgation: int = 0):
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
                    is_validated=True)

        users.append(user)
        total_players += 1

    owner = User['usuario{}@gmail.br'.format(total_players - players_cuantity)]

    # Create game and Board
    game = Game(name='test_game_{}'.format(games),
                owner=owner,
                min_players=5,
                max_players=10,
                creation_date=datetime.datetime.today(),
                chaos=False,
                state=game_state-1)
    games += 1

    Board(game=game,
          fenix_promulgation=fenix_promulgation,
          death_eater_promulgation=death_eater_promulgation,
          election_counter=0,
          spell_available=False)
    commit()

    game_id = game.id

    players = []
    turn = 1
    # Join players in game
    for user in users:

        is_Fenix = turn % 2 == 0
        is_Voldemort = turn % players_cuantity == 0
        player = Player(turn=turn,
                        user=user,
                        rol='Voldemort' if is_Voldemort else 'Fenix Order',
                        loyalty='Fenix Order' if is_Fenix and not is_Voldemort else 'Death Eater',
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

    # Start game with one turn if game_state is 0
    if start:
        response = client.put('game/{}/init?player_id={}'.format(game_id, players[0].id))
        

    candidate_id = players[0].id
    # Correcting bug about minister selection for endpoint "promulgate". Director should select!
    # This loop sets current minister id, so when using this id is relative to the game_factory turns
    # If that is not the case, returns the id that was set without these changes
    # So be careful here, directions are relative if you know that turns_cuantity > 0
    for _ in range(turns_cuantity):

        response = client.put('game/{}/select_MM'.format(game_id))
        response_keys = response.json().keys()
        if (response.json() is not None) and (not "detail" in response_keys) and ("candidate_minister_id" in response_keys):
            candidate_id = response.json()["candidate_minister_id"]

    return [game_id, candidate_id, total_players]


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


def start_new_turn(game_id: int):
    return client.put('game/{}/select_MM'.format(game_id))


def get_3_cards(game_id: int, player_id: int):
    return client.get(
        '/game/{}/minister_cards?player_id={}'.format(game_id, player_id)
    )


def check_game_state(game_id: int):
    return client.get('game/{}/check_game'.format(game_id))


def get_director_candidates(game_id: int):
    return client.get('/game/{}/director_candidates'.format(game_id))


def execute_spell(game_id: int, spell: str, minister_id: int, player_id: int):
    return client.put('/game/{}/execute_spell?spell={}'.format(game_id, spell), json={
        "minister_id": minister_id,
        "player_id": player_id
    }
    )


def player_vote(game_id: int, player_id: int, vote: int):
    return client.put('/game/{}/vote'.format(game_id), json={
        "id": player_id,
        "vote": vote
    }
    )


def director_promulgate(game_id: int, player_id: int, card_type: int):
    return client.put('/game/{}/promulgate'.format(game_id), json={
        "player_id": player_id,
        "to_promulgate": card_type
    }
    )


def set_director_candidate(game_id: int, minister_id: int, director_id: int):
    return client.put('/game/{}/select_director_candidate'.format(game_id), json={
        "minister_id": minister_id,
        "director_id": director_id
    }
    )


def start_expelliarmus(game_id: int, director_id: int):
    return client.put('/game/{}/director_expelliarmus?director_id={}'.format(game_id, director_id))


def consent_expelliarmus(game_id: int, minister_id: int, consent: bool):
    return client.put('/game/{}/minister_expelliarmus'.format(game_id), json={
        "minister_id": minister_id,
        "consent": consent
    }
    )


@db_session()
def get_player_by_id(player_id: int):
    return Player[player_id]


@db_session()
def check_players_roles(game_id: int):
    game = Game[game_id]
    for player in game.players:
        if (player.rol != "Fenix Order") and (player.rol != "Death Eater") and (player.rol != "Voldemort"):
            return 0
    return 1


@db_session()
def check_players_loyalty(game_id: int):
    game = Game[game_id]
    for player in game.players:
        if (player.loyalty != "Fenix Order") and (player.loyalty != "Death Eater"):
            return 0
    return 1


@db_session()
def count_roles_from_game(game_id: int, rol: str):
    game = Game[game_id]
    count = 0
    for player in game.players:
        if player.rol == rol:
            count = count+1
    return count


@db_session()
def users_factory(amount_users: int):

    global total_players
    users_email = []
    for user in range(amount_users):
        user = User(email='usuario{}@gmail.br'.format(total_players),
                    username='User_{}'.format(total_players),
                    password="fachero".encode(),
                    icon="".encode(),
                    creation_date=datetime.datetime.today(),
                    last_access_date=datetime.datetime.today(),
                    is_validated=True)
        total_players += 1
        users_email.append(user.email)

    return users_email


def start_new_game(game_params: GameParams):
    return client.post(
         'game/create/',
         json = game_params
     )


@db_session()
def is_player_in_game_by_id(game_id: int, player_id: int):
    return True if Player.get(
        lambda p: p.game_in.id == game_id and p.id == player_id) is not None else False


def join_a_game(game_id: int, user_email: EmailParameter):
     return client.put('game/{}/join'.format(game_id),
         json= user_email)


def init_the_game(game_id: int, player_id: int):
     return client.put('game/{}/init?player_id={}'.format(game_id, player_id))


def get_3_cards(game_id: int, player_id: int):
    return client.get(
        '/game/{}/minister_cards?player_id={}'.format(game_id, player_id)
    )


def card_discard(game_id: int, discard_data: DiscardData):
    return client.put(
        'game/{}/discard'.format(game_id),
        json = discard_data
    )


def get_not_discarded_cards(game_id:int, player_id: int):
    return client.get(
        "/game/{}/director_cards?player_id={}".format(game_id, player_id)
    )


def get_vote_formula(game_id: int):
    return client.get('/game/{}/get_candidates'.format(game_id))


def game_state_in_pregame(game_id: int, player_id: int):
    return client.get("/game/{}/initialized/?player_id={}".format(game_id, player_id))

def leave_game_not_initialized(game_id: int, user_email: EmailParameter):
    return client.put("/game/{}/leave_not_init_game".format(game_id),
                      json= user_email)
