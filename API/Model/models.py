from pydantic import BaseModel, Field, EmailStr, validator, StrictInt
from datetime import datetime

import API.Model.user_check as user_check


class User(BaseModel):
    email: EmailStr = Field(...)
    username: str   = Field(..., min_length=5, max_length=50)
    password: str   = Field(..., min_length=8, max_length=50)
    icon: bytes
    creation_date: datetime
    last_access_date: datetime
    is_validated: bool

    @validator("email")
    def email_size(cls, val):
        return user_check.email_size_validate(val)

    @validator("username")
    def username_char_set(cls, val):
        return user_check.username_char_set_validate(val)
    
    @validator("password")
    def no_space_in_string(cls, val):
        return user_check.no_space_in_string_validate(val)


class UserRegisterIn(BaseModel):
    email: EmailStr = Field(...)
    username: str   = Field(..., min_length=5, max_length=50)
    password: str   = Field(..., min_length=8, max_length=50)
    password_verify: str = Field(..., min_length=8, max_length=50)

    @validator("email")
    def email_size(cls, val):
        return user_check.email_size_validate(val)

    @validator("username")
    def username_char_set(cls, val):
        return user_check.username_char_set_validate(val)
    
    @validator("password")
    def no_space_in_string(cls, val):
        return user_check.no_space_in_string_validate(val)
    
    @validator("password_verify")
    def passwords_match(cls, val, values):
        if not ("password" in values):
            raise ValueError("password was not valid")
        if val != values["password"]:
            raise ValueError("passwords don't match")
        # We already know that password matched is valid
        return val


class UserProfile(BaseModel):
    email: EmailStr
    username: str
    last_access_date: datetime
    is_validated: bool


class UserUpdateUsername(BaseModel):
    email: EmailStr   = Field(...)
    new_username: str = Field(..., min_length=5, max_length=50)
    password: str        = Field(..., min_length=8, max_length=50)
    password_verify: str = Field(..., min_length=8, max_length=50)

    @validator("email")
    def email_size(cls, val):
        return user_check.email_size_validate(val)

    @validator("new_username")
    def username_char_set(cls, val):
        return user_check.username_char_set_validate(val)
    
    @validator("password")
    def no_space_in_string(cls, val):
        return user_check.no_space_in_string_validate(val)

    @validator("password_verify")
    def passwords_match(cls, val, values):
        if not ("password" in values):
            raise ValueError("password was not valid")
        if val != values["password"]:
            raise ValueError("passwords don't match")
        # We already know that password matched is valid
        return val


class UserUpdatePassword(BaseModel):
    email: EmailStr = Field(...)
    old_password: str        = Field(..., min_length=8, max_length=50)
    old_password_verify: str = Field(..., min_length=8, max_length=50)
    new_password: str        = Field(..., min_length=8, max_length=50)

    @validator("email")
    def email_size(cls, val):
        return user_check.email_size_validate(val)
    
    @validator("old_password", "new_password")
    def no_space_in_string(cls, val):
        return user_check.no_space_in_string_validate(val)

    @validator("old_password_verify")
    def passwords_match(cls, val, values):
        if not ("old_password" in values):
            raise ValueError("old_password was not valid")
        if val != values["old_password"]:
            raise ValueError("passwords don't match")
        # We already know that password matched is valid
        return val
    
    @validator("new_password")
    def new_password_not_equal_to_old_password(cls, val, values):
        if not ("old_password" in values):
            raise ValueError("old_password was not valid")
        if not ("old_password_verify" in values):
            raise ValueError("old_password_verify was not valid")
        if val == values["old_password"]:
            raise ValueError("new_password can not be equal to old password")
        return val


class UserUpdateIcon(BaseModel):
    email: EmailStr = Field(...)
    password: str        = Field(..., min_length=8, max_length=50)
    password_verify: str = Field(..., min_length=8, max_length=50)

    @validator("email")
    def email_size(cls, val):
        return user_check.email_size_validate(val)

    @validator("password")
    def no_space_in_string(cls, val):
        return user_check.no_space_in_string_validate(val)

    @validator("password_verify")
    def passwords_match(cls, val, values):
        if not ("password" in values):
            raise ValueError("password was not valid")
        if val != values["password"]:
            raise ValueError("passwords don't match")
        # We already know that password matched is valid
        return val


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
