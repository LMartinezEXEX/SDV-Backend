import Database.turn_functions as db_turn
import Database.player_functions as db_player
import Database.game_functions as db_game
import API.Model.voteAPI as model_vote
from API.Model.exceptions import *
from API.Model.models import *
from API.Model.game_check import *

def check_and_get_player_ids(game_id: int):
    check_game_state(game_id)

    return {"Player ids": db_game.get_all_players_id(game_id)}


def check_and_get_players_info(game_id: int):
    check_game_state(game_id)

    return {"Players info": db_game.get_players_info(game_id)}


def check_and_reject_notify(game_id: int, player_id: int):
    if not db_game.get_game_by_id(game_id=game_id):
        raise game_not_found_exception

    vote_result = model_vote.check_and_get_vote_result(game_id)

    # If candidates were elected then don't notify
    if vote_result["result"]:
        return { "notified": False }

    return db_player.notify_with_player(game_id, player_id)
