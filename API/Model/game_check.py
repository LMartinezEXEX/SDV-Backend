from API.Model.exceptions import *
from Database.game_functions import *
from Database.turn_functions import *

def check_game_state(game_id: int):
    state = get_game_state(game_id)

    # Game not found
    if state == -1:
        raise game_not_found_exception

    # Game not started
    if state == 0:
        raise game_not_started_exception

    # Game finished
    if state == 2:
        raise game_has_finished_exception


def check_game_with_at_least_one_turn(game_id: int):
    check_game_state(game_id)

    turns = get_current_turn_number_in_game(game_id)

    if turns == 0:
        raise turn_hasnt_started_exception
