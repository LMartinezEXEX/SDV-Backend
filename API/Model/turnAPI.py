import Database.turn_functions as db_turn
import Database.board_functions as db_board
import Database.game_functions as db_game
from API.Model.exceptions import *
from API.Model.models import *
from API.Model.game_check import *


def get_next_MM(game_id: int):
    check_game_state(game_id)

    if db_board.is_board_available_spell(game_id):
        raise spell_not_used_exception

    return {
        "candidate_minister_id": db_turn.select_MM_candidate(game_id)}


def check_and_get_director_candidates(game_id: int):
    check_game_with_at_least_one_turn(game_id)

    return {"director candidates": db_turn.director_available_candidates(game_id)}


def check_and_set_director_candidate(game_id, minister_id, director_id):
    check_game_with_at_least_one_turn(game_id)

    # Player is not current minister
    if not db_turn.is_current_minister(game_id, minister_id):
        raise player_isnt_minister_exception

    # Alredy selected director candidate
    if db_turn.already_selected_director_candidate(game_id):
        raise director_candidate_already_set_exception

    formula = db_turn.select_DD_candidate(game_id, director_id)

    return {"candidate minister id": formula[0], "candidate director id": formula[1]}


def get_vote_candidates(game_id: int):
    if not db_game.get_game_by_id(game_id=game_id):
        raise geme_not_found_exception
    candidates = db_turn.get_candidates(game_id=game_id)
    return TurnFormula(
        minister_id = candidates[0],
        director_id = candidates[1]
    )
