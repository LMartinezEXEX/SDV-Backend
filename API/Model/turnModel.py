import Database.turn_functions
from fastapi import HTTPException, status

def get_next_MM(game_id: int):
    return {"candidate_minister_id": Database.turn_functions.select_MM_candidate(game_id)}


def vote_candidate(game_id: int, player_id: int, vote: bool):
    is_alive = Database.turn_functions.is_alive(game_id, player_id)

    # Player is alive and hasn't vote
    if is_alive and not Database.turn_functions.player_voted(game_id, player_id):
        current_vote_cuantity = Database.turn_functions.vote_turn(game_id, player_id, vote)
        return {"votes": current_vote_cuantity}

    # Player isn't alive
    elif not is_alive:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail = "Player is dead")

    # Player already voted
    else:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail = "Player already voted")


def get_vote_result(game_id: int):
    current_alive_players = Database.turn_functions.alive_players(game_id)
    current_votes = Database.turn_functions.current_votes(game_id)

    # Every player voted
    if current_votes == current_alive_players:
        vote_result = Database.turn_functions.get_result(game_id)
        result = vote_result[0]
        voted_lumos = vote_result[1]

        return {"result": result, "voted_lumos": voted_lumos}

    # Some player hasn't voted
    else:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail = "Vote's missing")


def get_3_cards(game_id):
    return {"cards": Database.turn_functions.generate_3_cards(game_id)}
