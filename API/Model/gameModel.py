from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator
from fastapi import Depends, HTTPException
from Database import database
from Database.game_functions import *
from API.Model.gameExceptions import *
from Database.turn_functions import create_first_turn, get_current_minister
from typing import List


class GameParams(BaseModel):
    email: EmailStr
    name: str
    min_players: int
    max_players: int


class EmailParameter(BaseModel):
    email: EmailStr


class Game_to_List(BaseModel):
    id: int
    owner: str
    name: str
    min_players: int
    max_players: int
    players: int


def list_available_games():
    g_list = get_game_list()
    if not g_list:
        raise not_games_available_exception
    return g_list 


def create_new_game(game_params: GameParams):
    check_create_conditions(user_email=game_params.email, name=game_params.name,
                            min_players=game_params.min_players, max_players=game_params.max_players)
    game_id = save_new_game(owner=game_params.email, name=game_params.name,
                            min_players=game_params.min_players,
                            max_players=game_params.max_players)
    player_id = put_new_player_in_game(user=game_params.email, game_id=game_id)
    return {"Game_Id": game_id, "Player_Id": player_id}


def join_game_with_keys(game_id: int, user_email: EmailStr):
    check_join_conditions(game_id=game_id, user_email=user_email)
    player_id = put_new_player_in_game(user=user_email, game_id=game_id)
    return {"Player_Id": player_id}


def init_game_with_ids(game_id: int, player_id: int):
    check_init_conditions(game_id=game_id, player_id=player_id)
    minister_id = create_first_turn(game_id=game_id)
    amount_players = players_in_game(game_id=game_id)
    rol_and_loyalty = get_player_rol_and_loyalty(player_id=player_id)
    return {"game_state": 1, "minister_id": minister_id, "amount_of_players": amount_players,
           "rol": rol_and_loyalty.get("Rol"), "loyalty": rol_and_loyalty.get("Loyalty")}


def check_if_game_started(game_id: int, player_id: int):
    if not is_player_in_game_by_id(game_id=game_id, player_id=player_id):
        raise player_not_in_game_exception
    state = get_game_state(game_id)
    users = get_current_users_in_game(game_id=game_id)
    if not state or state == 2:
        return {"game_state": state, "users": users}
    else:
        minister_id = get_current_minister(game_id=game_id)
        amount_players = players_in_game(game_id=game_id)
        rol_and_loyalty = get_player_rol_and_loyalty(player_id=player_id)
        users = get_current_users_in_game(game_id=game_id)
        return {"game_state": state, "minister_id": minister_id, "amount_of_players": amount_players,
           "rol": rol_and_loyalty.get("Rol"), "loyalty": rol_and_loyalty.get("Loyalty"), "users": users}

        



