from API.Model.game_check import *
import Database.turn_functions as db_turn
import Database.board_functions as db_board

def promulgate_in_game(game_id: int, director_id: int, card_type: int):
    check_game_with_at_least_one_turn(game_id)

    current_turn = db_turn.get_current_turn_in_game(game_id)

    # Expelliarmus is set in current turn
    if db_turn.is_expelliarmus_set(game_id) and current_turn.minister_consent == 2:
        raise cant_promulgate_expelliarmus_exception

    # Already promulgated in this turn
    if db_turn.already_promulgate_in_current_turn(game_id):
        raise already_promulgated_in_turn_exception

    # Player is not current director
    if not db_turn.is_current_director(game_id, director_id):
        raise player_isnt_director_exception

    board_state = db_board.promulgate(game_id, card_type)

    return {"fenix promulgations": board_state[0],
            "death eater promulgations": board_state[1]}
