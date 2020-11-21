from pydantic import EmailStr
import Database.game_functions as db_game
import Database.turn_functions as db_turn
import Database.player_functions as db_player
from API.Model.exceptions import *
from API.Model.game_check import *
from API.Model.models import *


def list_available_games():
    g_list = db_game.get_game_list()
    if not g_list:
        raise not_games_available_exception
    return g_list


def create_new_game(game_params: GameParams):
    db_game.check_create_conditions(user_email=game_params.email, name=game_params.name,
                            min_players=game_params.min_players, max_players=game_params.max_players)
    game_id = db_game.save_new_game(owner=game_params.email, name=game_params.name,
                            min_players=game_params.min_players,
                            max_players=game_params.max_players)
    player_id = db_player.put_new_player_in_game(user=game_params.email, game_id=game_id)
    return {"Game_Id": game_id, "Player_Id": player_id}


def join_game_with_keys(game_id: int, user_email: EmailStr):
    db_game.check_join_conditions(game_id=game_id, user_email=user_email)
    player_id = db_player.put_new_player_in_game(user=user_email, game_id=game_id)
    return {"Player_Id": player_id}


def init_game_with_ids(game_id: int, player_id: int):
    db_game.check_init_conditions(game_id=game_id, player_id=player_id)
    minister_id = db_turn.create_first_turn(game_id=game_id)
    db_game.assign_roles(game_id=game_id)
    amount_players = db_game.players_in_game(game_id=game_id)
    rol_and_loyalty = db_player.get_player_rol_and_loyalty(player_id=player_id)
    return {"game_state": 1, "minister_id": minister_id, "amount_of_players": amount_players,
           "rol": rol_and_loyalty.get("Rol"), "loyalty": rol_and_loyalty.get("Loyalty")}


def check_if_game_started(game_id: int, player_id: int):
    if not db_player.is_player_in_game_by_id(game_id=game_id, player_id=player_id):
        raise player_not_in_game_exception
    state = db_game.get_game_state(game_id)
    users = db_game.get_current_users_in_game(game_id=game_id)
    if not state or state == 2:
        return {"game_state": state, "users": users}
    else:
        minister_id = db_turn.get_current_minister(game_id=game_id)
        amount_players = db_game.players_in_game(game_id=game_id)
        rol_and_loyalty = db_player.get_player_rol_and_loyalty(player_id=player_id)
        users = db_game.get_current_users_in_game(game_id=game_id)
        return {"game_state": state, "minister_id": minister_id, "amount_of_players": amount_players,
           "rol": rol_and_loyalty.get("Rol"), "loyalty": rol_and_loyalty.get("Loyalty"), "users": users}


def game_status(game_id: int):
    check_game_state(game_id)

    status = db_game.check_status(game_id)

    return {"game id": game_id,
            "finished": status[0],
            "fenix promulgations": status[1],
            "death eater promulgations": status[2],
            "current minister id": status[3],
            "current director id": status[4],
            "vote done": status[5],
            "expelliarmus": status[6],
            "minister consent": status[7]}
