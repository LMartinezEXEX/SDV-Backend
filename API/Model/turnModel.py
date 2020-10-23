import Database.turn_functions
from fastapi import HTTPException, status

def get_next_MM(game_id: int):
    return {"candidate_minister_id": Database.turn_functions.select_MM_candidate(game_id)}
