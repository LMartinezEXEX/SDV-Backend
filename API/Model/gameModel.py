from typing   import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator
from fastapi  import Depends, HTTPException
from Database import database
from Database.game_functions import *


class GameParams(BaseModel):
    email: EmailStr
    name: str
    min_players: int
    max_players: int


class JoinModel(BaseModel):
    game_id: int
    user_email: EmailStr

# op = 0 -> Cant find data
# op = 1 -> Success 
class OpResponse(BaseModel):
    op: int
    message: str


class InitGameIds(BaseModel):
    player_id: int
    game_id: int



def create_new_game(game_params: GameParams):
    game_id = save_new_game(owner=game_params.email, name=game_params.name, 
                            min_players=game_params.min_players,
                            max_players=game_params.max_players)
    if not game_id:
        return 0
    if not put_new_player_in_game(user=game_params.email, game_id=game_id):
        return 0
    return game_id


def join_game_with_keys(keys: JoinModel):
    if put_new_player_in_game(keys.user_email, keys.game_id):
        return OpResponse(
            op = 1,
            message = "Game successfully joined"
        )   
    else:
        return OpResponse(
            op = 0,
            message = "Cant join game"
        )
        


def init_game_with_ids(ids: InitGameIds):
    if not get_game_by_id(game_id=ids.game_id):
        return OpResponse(
            op = 0,
            message = "Cant find game"
        )
    # This should not happen. If the player can start the game, its because the player exists
    if not get_player_by_id(player_id=ids.player_id):
        return OpResponse(
            op = 0,
            message = "Cant find player"
        )
    if check_init_conditions(game_id=ids.game_id, player_id=ids.player_id):
        with db_session:
            Game[ids.game_id].state = 1
        return OpResponse(
            op = 1,
            message = "The game has started! Have fun!"
        )
    else:
        return OpResponse(
            op = 1,
            message = "The game has not reach the minimum amount of players"
        )




