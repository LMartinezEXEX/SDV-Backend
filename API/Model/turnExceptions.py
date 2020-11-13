from fastapi import HTTPException, status

game_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Game doesn't exist"
)

game_not_started_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Game hasn't started"
)

game_finished_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Game finished"
)

invalid_player_in_game_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Player is not in this game"
)

player_is_dead_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Player is dead"
)

player_already_voted_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Player already voted"
)

votes_missing_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Vote's missing"
)

cards_taken_in_current_turn_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Already taken the cards in this turn"
)

turn_hasnt_started_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="No turn started yet"
)

already_promulgated_in_turn_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Minister already promulgated in this turn"
)

player_isnt_minister_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Player is not minister"
)

didnt_promulgate_in_turn_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Must promulgate in current turn before execute a spell"
)

no_spell_available_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The requirements to cast the spell are not met"
)

player_already_investigated_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Player has been already investigated"
)

spell_not_used_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="A spell is available and need to be used before start of next turn"
)

director_candidate_already_set_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Already set director candidate in current turn"
)


#-------------- Tomás Exceptions -------------------------

invalid_card_type_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The type of the card to discard is invalid"
)

player_isnt_director_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Player is not director"
)

not_discarded_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Player is not director"
)