from typing   import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator
from fastapi  import Depends, HTTPException
from Database import database


class GameParams(BaseModel):
    email: EmailStr
    name: str
    min_players: int
    max_players: int


class JoinModel(BaseModel):
    game_id: int
    user_id: int

# op = 0 -> Cant find data
# op = 1 -> Success 
class OpResponse(BaseModel):
    op: int
    message: str


class InitGameIds(BaseModel):
    player_id: int
    game_id: int
