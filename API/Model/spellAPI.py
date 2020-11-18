from enum import Enum
from API.Model.game_check import *
from API.Model.models import *
import Database.turn_functions as db_turn
import Database.board_functions as db_board
import Database.spell_functions as db_spell
import Database.player_functions as db_player

class Spell(str, Enum):
    GUESSING = "Guessing"
    CRUCIO = "Crucio"
    AVADA_KEDAVRA = "Avada Kedavra"


def check_and_get_available_spell(game_id: int):
    check_game_state(game_id)

    if db_turn.get_current_turn_number_in_game(game_id) == 0 or (
            not db_board.is_board_available_spell(game_id)):
        spell = ""

    else:
        spell = db_spell.available_spell_in_game_conditions(game_id)

    return {"Spell": spell}


def check_spell_base_conditions(game_id: int, minister_id: int):
    check_game_with_at_least_one_turn(game_id)

    if not db_turn.already_promulgate_in_current_turn(game_id):
        raise didnt_promulgate_in_turn_exception

    if not db_turn.is_current_minister(game_id, minister_id):
        raise player_isnt_minister_exception

    if not db_board.is_board_available_spell(game_id):
        raise no_spell_available_exception


def check_and_execute_guessing(game_id: int, spell_data: SpellData):
    check_spell_base_conditions(game_id, spell_data.minister_id)

    return {"cards": db_spell.execute_guessing(game_id)}


def check_and_execute_crucio(game_id: int, spell_data: SpellData):
    check_spell_base_conditions(game_id, spell_data.minister_id)

    if not db_player.is_player_in_game_by_id(game_id, spell_data.player_id):
        raise invalid_player_in_game_exception

    if not db_player.is_alive(game_id, spell_data.player_id):
        raise player_is_dead_exception

    if db_player.is_player_investigated(spell_data.player_id):
        raise player_already_investigated_exception

    return {"Fenix loyalty": db_spell.execute_crucio(game_id, spell_data.player_id)}


def check_and_execute_avada_kedavra(game_id: int, spell_data: SpellData):
    check_spell_base_conditions(game_id, spell_data.minister_id)

    if not db_player.is_player_in_game_by_id(game_id, spell_data.player_id):
        raise invalid_player_in_game_exception

    if not db_player.is_alive(game_id, spell_data.player_id):
        raise player_is_dead_exception

    return {"Finished": db_spell.execute_avada_kedavra(game_id, spell_data.player_id)}
