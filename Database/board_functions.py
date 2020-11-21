from pony import orm
from Database.database import *
import Database.turn_functions as db_turn
import Database.spell_functions as db_spell


@orm.db_session
def fenix_promulgations_count(game_id):
    '''
    Get amount of fenix promulgations in current turn
    '''

    return Board[game_id].fenix_promulgation


@orm.db_session
def deth_eater_promulgations_count(game_id):
    '''
    Get amount of death eater promulgations in current turn
    '''

    return Board[game_id].death_eater_promulgation


@orm.db_session
def is_board_available_spell(game_id):
    '''
    Assert if there is an available spell to execute
    '''

    return Board[game_id].spell_available




@orm.db_session
def promulgate(game_id: int, card_type: int):
    '''
    Promulgate a card given by the current minister in the game
    If card_type = 0, promulgate for the Fenix Order
    If card_type = 1, promulgate for the Death Eaters
    '''

    turn_number = db_turn.get_current_turn_number_in_game(game_id)
    turn = db_turn.get_turn_in_game(game_id, turn_number)

    board = Board[game_id]
    # Restart board counter
    board.election_counter = 0

    if card_type:
        board.death_eater_promulgation += 1
        db_spell.check_available_spell(game_id)
    else:
        board.fenix_promulgation += 1

    turn.promulgated = True
    return [board.fenix_promulgation, board.death_eater_promulgation]
