from fastapi import HTTPException, status

# This should be in UserException
user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)
#-----------------------------

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