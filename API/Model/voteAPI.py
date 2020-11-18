from API.Model.models import *
import Database.player_functions as db_player
import Database.vote_functions as db_vote
import Database.game_functions as db_game
from API.Model.game_check import *


def check_and_vote_candidate(game_id: int, player_id: int, vote: bool):
    check_game_with_at_least_one_turn(game_id)

    # player isn't in this game
    if not db_player.is_player_in_game_by_id(game_id, player_id):
        raise invalid_player_in_game_exception

    is_alive = db_player.is_alive(game_id, player_id)

    # Player is alive and hasn't vote
    if is_alive and not db_player.player_voted(
            game_id, player_id):
        current_vote_cuantity = db_vote.vote_turn(
            game_id, player_id, vote)
        return {"votes": current_vote_cuantity}

    # Player is dead
    elif not is_alive:
        raise player_is_dead_exception

    # Player already voted
    else:
        raise player_already_voted_exception


def check_and_get_vote_result(game_id: int):
    check_game_with_at_least_one_turn(game_id)

    current_alive_players = db_game.alive_players_count(
        game_id)
    current_votes = db_vote.current_votes(game_id)

    # Every player voted
    if current_votes == current_alive_players:
        vote_result = db_vote.get_result(game_id)
        result = vote_result[0]
        voted_lumos = vote_result[1]

        return {"result": result, "voted_lumos": voted_lumos}

    # Some player hasn't voted
    else:
        raise votes_missing_exception
