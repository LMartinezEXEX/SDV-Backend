import Database.turn_functions
from pydantic import BaseModel, StrictInt
from API.Model.turnExceptions import *


class PlayerVote(BaseModel):
    id: int
    vote: bool


class PlayerPromulgate(BaseModel):
    candidate_id: int
    to_promulgate: StrictInt


def check_game_state(game_id):
    state = Database.turn_functions.get_game_state(game_id)

    # Game not found
    if state == -1:
        raise game_not_found_exception

    # Game not started
    if state == 0:
        raise game_not_started_exception

    # Game finished
    if state == 2:
        raise game_finished_exception


def get_next_MM(game_id: int):
    check_game_state(game_id)
    return {
        "candidate_minister_id": Database.turn_functions.select_MM_candidate(game_id)}


def check_and_vote_candidate(game_id: int, player_id: int, vote: bool):
    check_game_state(game_id)

    # player isn't in this game
    if not Database.turn_functions.is_player_in_game(game_id, player_id):
        raise invalid_player_in_game_exception

    is_alive = Database.turn_functions.is_alive(game_id, player_id)

    # Player is alive and hasn't vote
    if is_alive and not Database.turn_functions.player_voted(
            game_id, player_id):
        current_vote_cuantity = Database.turn_functions.vote_turn(
            game_id, player_id, vote)
        return {"votes": current_vote_cuantity}

    # Player is dead
    elif not is_alive:
        raise player_is_dead_exception

    # Player already voted
    else:
        raise player_already_voted_exception


def check_and_get_vote_result(game_id: int):
    check_game_state(game_id)

    current_alive_players = Database.turn_functions.alive_players_count(game_id)
    current_votes = Database.turn_functions.current_votes(game_id)

    # Every player voted
    if current_votes == current_alive_players:
        vote_result = Database.turn_functions.get_result(game_id)
        result = vote_result[0]
        voted_lumos = vote_result[1]

        return {"result": result, "voted_lumos": voted_lumos}

    # Some player hasn't voted
    else:
        raise votes_missing_exception


def check_and_get_3_cards(game_id):
    check_game_state(game_id)

    # Game has at least one turn
    if Database.turn_functions.get_current_turn_number_in_game(game_id) != 0:

        # Cards were taken in this turn
        if Database.turn_functions.taked_cards(game_id):

            raise cards_taken_in_current_turn_exception

        else:
            return {"cards": Database.turn_functions.generate_3_cards(game_id)}

    else:
        raise turn_hasnt_started_exception


def promulgate_in_game(game_id, minister_id, card_type):
    check_game_state(game_id)

    # Already promulgated in this turn
    if Database.turn_functions.already_promulgate_in_current_turn(game_id):
        raise already_promulgated_in_turn_exception

    # Player is not current minister
    if not Database.turn_functions.is_current_minister(game_id, minister_id):
        raise player_isnt_minister_exception

    board_state = Database.turn_functions.promulgate(game_id, card_type)

    return {"fenix promulgations": board_state[0],
            "death eater promulgations": board_state[1]}


def game_status(game_id):
    check_game_state(game_id)

    status = Database.turn_functions.check_status(game_id)

    return {"finished": status[0],
            "fenix promulgations": status[1],
            "death eater promulgations": status[2],
            "current minister id": status[3],
            "current director id": status[4]}
