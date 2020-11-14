from enum import Enum
import Database.turn_functions as db_turn
from Database.game_functions import get_game_state, is_player_in_game_by_id, get_game_by_id
from pydantic import BaseModel, StrictInt
from API.Model.turnExceptions import *


class PlayerVote(BaseModel):
    id: int
    vote: bool


class PlayerPromulgate(BaseModel):
    candidate_id: int
    to_promulgate: StrictInt


class Spell(str, Enum):
    GUESSING = "Guessing"
    CRUCIO = "Crucio"


class SpellData(BaseModel):
    minister_id: int
    player_id: int


class TurnFormula(BaseModel):
    minister_id: int
    director_id: int


class DiscardData(BaseModel):
    player_id: int
    to_discard: int


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
        raise game_finished_exception


# Check game is 'IN GAME' and has at least one turn started

def check_game_with_at_least_one_turn(game_id: int):
    check_game_state(game_id)

    turns = db_turn.get_current_turn_number_in_game(game_id)

    if turns == 0:
        raise turn_hasnt_started_exception


def check_and_get_player_ids(game_id: int):
    check_game_state(game_id)

    return {"Player ids": db_turn.get_all_players_id(game_id)}


def check_and_get_players_info(game_id: int):
    check_game_state(game_id)

    return {"Players info": db_turn.get_players_info(game_id)}


def get_next_MM(game_id: int):
    check_game_state(game_id)

    if db_turn.is_board_available_spell(game_id):
        raise spell_not_used_exception

    return {
        "candidate_minister_id": db_turn.select_MM_candidate(game_id)}


def check_and_vote_candidate(game_id: int, player_id: int, vote: bool):
    check_game_with_at_least_one_turn(game_id)

    # player isn't in this game
    if not is_player_in_game_by_id(game_id, player_id):
        raise invalid_player_in_game_exception

    is_alive = db_turn.is_alive(game_id, player_id)

    # Player is alive and hasn't vote
    if is_alive and not db_turn.player_voted(
            game_id, player_id):
        current_vote_cuantity = db_turn.vote_turn(
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

    current_alive_players = db_turn.alive_players_count(
        game_id)
    current_votes = db_turn.current_votes(game_id)

    # Every player voted
    if current_votes == current_alive_players:
        vote_result = db_turn.get_result(game_id)
        result = vote_result[0]
        voted_lumos = vote_result[1]

        return {"result": result, "voted_lumos": voted_lumos}

    # Some player hasn't voted
    else:
        raise votes_missing_exception


def check_and_get_3_cards(game_id: int):
    check_game_with_at_least_one_turn(game_id)

    # Cards were taken in this turn
    if db_turn.taked_cards(game_id):

        raise cards_taken_in_current_turn_exception

    else:
        return {"cards": db_turn.generate_3_cards(game_id)}


def promulgate_in_game(game_id: int, minister_id: int, card_type: int):
    check_game_with_at_least_one_turn(game_id)

    # Already promulgated in this turn
    if db_turn.already_promulgate_in_current_turn(game_id):
        raise already_promulgated_in_turn_exception

    # Player is not current minister
    if not db_turn.is_current_minister(game_id, minister_id):
        raise player_isnt_minister_exception

    board_state = db_turn.promulgate(game_id, card_type)

    return {"fenix promulgations": board_state[0],
            "death eater promulgations": board_state[1]}


def game_status(game_id: int):
    check_game_state(game_id)

    status = db_turn.check_status(game_id)

    return {"game id": game_id,
            "finished": status[0],
            "fenix promulgations": status[1],
            "death eater promulgations": status[2],
            "current minister id": status[3],
            "current director id": status[4]}


def check_and_get_available_spell(game_id: int):
    check_game_state(game_id)

    if db_turn.get_current_turn_number_in_game(game_id) == 0 or (
            not db_turn.is_board_available_spell(game_id)):
        spell = ""

    else:
        spell = db_turn.available_spell_in_game_conditions(game_id)

    return {"Spell": spell}


def check_spell_base_conditions(game_id: int, minister_id: int):
    check_game_with_at_least_one_turn(game_id)

    if not db_turn.already_promulgate_in_current_turn(game_id):
        raise didnt_promulgate_in_turn_exception

    if not db_turn.is_current_minister(game_id, minister_id):
        raise player_isnt_minister_exception

    if not db_turn.is_board_available_spell(game_id):
        raise no_spell_available_exception


def check_and_execute_guessing(game_id: int, minister_id: int):
    check_spell_base_conditions(game_id, minister_id)

    return {"cards": db_turn.execute_guessing(game_id)}


def check_and_execute_crucio(game_id: int, minister_id: int, player_id: int):
    check_spell_base_conditions(game_id, minister_id)

    if not is_player_in_game_by_id(game_id, player_id):
        raise invalid_player_in_game_exception

    if not db_turn.is_alive(game_id, player_id):
        raise player_is_dead_exception

    if db_turn.is_player_investigated(player_id):
        raise player_already_investigated_exception

    return {"Fenix loyalty": db_turn.execute_crucio(game_id, player_id)}

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
    if not get_game_by_id(game_id=game_id):
        raise geme_not_found_exception
    candidates = db_turn.get_candidates(game_id=game_id)
    return TurnFormula(
        minister_id = candidates[0],
        director_id = candidates[1]
    )


def discard_selected_card(game_id: int, discard_data: DiscardData):
    if not get_game_by_id(game_id=game_id):
        raise game_not_found_exception
    if not db_turn.is_current_minister(game_id=game_id, player_id=discard_data.player_id):
        raise player_isnt_minister_exception
    return db_turn.discard_card(game_id=game_id, data=discard_data.to_discard)


def get_cards_for_director(game_id: int, player_id: int):
    if not get_game_by_id(game_id=game_id):
        raise game_not_found_exception
    if not db_turn.is_current_director(game_id=game_id, player_id=player_id):
        raise player_isnt_director_exception
    return {"cards": db_turn.get_not_discarded_cards(game_id=game_id)}
