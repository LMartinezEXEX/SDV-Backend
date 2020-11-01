from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator
from fastapi import Depends, HTTPException
from Database import database
from Database.game_functions import *
from API.Model.gameExceptions import *


class GameParams(BaseModel):
    email: EmailStr
    name: str
    min_players: int
    max_players: int


class EmailParameter(BaseModel):
    email: EmailStr


def create_new_game(game_params: GameParams):
    if game_params.min_players < 5:
        raise less_than_five_players_exception
    if game_params.max_players < game_params.min_players:
        raise incoherent_amount_of_players_exception
    if game_params.max_players > 10:
        raise more_than_ten_players_exception
    user = get_user_by_email(game_params.email)
    if not user:
        raise user_not_found_exception
    game_id = save_new_game(owner=game_params.email, name=game_params.name,
                            min_players=game_params.min_players,
                            max_players=game_params.max_players)
    player_id = put_new_player_in_game(user=game_params.email, game_id=game_id)
    return {"Game_Id": game_id, "Player_Id": player_id}


def join_game_with_keys(game_id: int, user_email: EmailStr):
    game = get_game_by_id(game_id=game_id)
    if not game:
        raise game_not_found_exception
    user = get_user_by_email(email=user_email)
    if not user:
        raise user_not_found_exception
    player_id = put_new_player_in_game(user=user_email, game_id=game_id)
    return {"Player_Id": player_id}


def init_game_with_ids(game_id: int, player_id: int):
    if not get_game_by_id(game_id=game_id):
        raise game_not_found_exception
    if not get_player_by_id(player_id=player_id):
        raise player_not_found_exception
    # check_game_status
    if check_init_conditions(game_id=game_id, player_id=player_id):
        with db_session:
            Game[game_id].state = 1
    else:
        raise min_player_not_reach_exception
