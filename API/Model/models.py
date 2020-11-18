from pydantic import BaseModel, Field, EmailStr, validator, StrictInt
from datetime import datetime

class User(BaseModel):
    email: EmailStr
    username: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=8, max_length=50)
    icon: bytes
    creation_date: datetime
    last_access_date: datetime
    is_validated: bool

    @validator("email")
    def email_size(cls, val):
        if len(val) > 100:
            raise ValueError("Length of email is greater than 100")
        if len(val) < 10:
            raise ValueError("Length of email is less tan 10")
        return val

class UserRegisterIn(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserProfile(BaseModel):
    email: EmailStr
    username: str
    last_access_date: datetime
    is_validated: bool


class UserUpdateUsername(BaseModel):
    email: EmailStr
    new_username: str
    password: str


class UserUpdatePassword(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str


class UserUpdateIcon(BaseModel):
    email: EmailStr
    password: str


class GameParams(BaseModel):
    email: EmailStr
    name: str
    min_players: int
    max_players: int


class EmailParameter(BaseModel):
    email: EmailStr


class Game_to_List(BaseModel):
    id: int
    owner: str
    name: str
    min_players: int
    max_players: int
    players: int


class PlayerVote(BaseModel):
    id: int
    vote: bool


class PlayerPromulgate(BaseModel):
    player_id: int
    to_promulgate: StrictInt


class SpellData(BaseModel):
    minister_id: int
    player_id: int


class TurnFormula(BaseModel):
    minister_id: int
    director_id: int


class DiscardData(BaseModel):
    player_id: int
    to_discard: int
