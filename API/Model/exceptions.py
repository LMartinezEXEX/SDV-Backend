from fastapi import HTTPException, status

not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)

register_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Could not register the user"
)

update_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Failed to update"
)

update_icon_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Failed to update icon. Formats allowed: jpeg, png, bmp, webp"
)

unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
)

not_authenticated_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not authenticated"
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)

profile_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Login to see private profile"
)

user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)

game_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Game not found"
)

player_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Player not found"
)

player_not_in_game_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The player is not in the game"
)

player_already_in_game_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The user is already in game"
)

less_than_five_players_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The game must have at least 5 players"
)

more_than_ten_players_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The game must have less than 10 players"
)

min_player_not_reach_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The game has not reach the minimum amount of players"
)

not_the_owner_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You cant start the game, you are not the owner!"
)

max_players_reach_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The game has reach the maximum amount of players"
)

game_has_started_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The game has started"
)

game_has_finished_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The game has finished"
)

game_not_deleted_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The game has not been deleted"
)

game_not_started_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Game hasn't started"
)

incoherent_amount_of_players_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The minimum of players is higher than the maximum"
)

inconsistent_amount_of_players_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The amount of players is inconsistent to assign roles"
)

not_games_available_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="There are no games available"
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

cards_not_taken_in_current_turn_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cards were not taken by minister in this turn"
)

turn_hasnt_started_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="No turn started yet"
)

already_promulgated_in_turn_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Director already promulgated in this turn"
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
    detail="Card was not discarded"
)

expelliarmus_already_set = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Expelliarmus was already set in current turn"
)

expelliarmus_promulgations_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Expelliarmus requires 5 death eater promulgations"
)

expelliarmus_not_set_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Director didnt propose a Expelliarmus"
)

consent_already_given_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Consent already given"
)
