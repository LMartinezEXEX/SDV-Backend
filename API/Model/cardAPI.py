from API.Model.exceptions import *
from API.Model.game_check import *
from API.Model.models import *
import Database.game_functions as db_game
import Database.turn_functions as db_turn
import Database.card_functions as db_card

def check_and_get_3_cards(game_id: int, player_id: int):
    check_game_with_at_least_one_turn(game_id)

    # Cards were taken in this turn
    if db_turn.taked_cards(game_id):
        raise cards_taken_in_current_turn_exception

    if not db_turn.is_current_minister(game_id, player_id):
        raise player_isnt_minister_exception

    return {"cards": db_card.generate_3_cards(game_id)}

def discard_selected_card(game_id: int, discard_data: DiscardData):
    if not db_game.get_game_by_id(game_id=game_id):
        raise game_not_found_exception
    if not db_turn.is_current_minister(game_id=game_id, player_id=discard_data.player_id):
        raise player_isnt_minister_exception
    return db_card.discard_card(game_id=game_id, data=discard_data.to_discard)


def get_cards_for_director(game_id: int, player_id: int):
    if not db_game.get_game_by_id(game_id=game_id):
        raise game_not_found_exception
    if not db_turn.is_current_director(game_id=game_id, player_id=player_id):
        raise player_isnt_director_exception
    if not db_turn.taked_cards(game_id):
        raise cards_not_taken_in_current_turn_exception
    if not db_turn.director_cards_set(game_id):
        raise not_discarded_exception

    return {"cards": db_card.get_not_discarded_cards(game_id=game_id)}
