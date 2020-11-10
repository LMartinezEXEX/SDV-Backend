# Imports
import json
from imghdr import what
from itertools import chain
from datetime import datetime, timedelta
from typing import Optional
from http.cookies import SimpleCookie
from pydantic import EmailStr
from fastapi import FastAPI, Header, Depends, Form, File, UploadFile, Response, status, Body
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import OAuth2PasswordRequestForm
from USER_URLS import USER_REGISTER_URL, USER_LOGIN_URL, USER_LOGOUT_URL, USER_PROFILE_URL,\
     USER_ICON_URL, USER_UPDATE_USERNAME_URL, USER_UPDATE_PASSWORD_URL, USER_UPDATE_ICON_URL

# User Model
from API.Model.userModel import UserRegisterIn, UserProfile,\
    UserUpdateUsername, UserUpdatePassword, UserUpdateIcon,\
    get_user_profile_by_email, get_user_icon_by_email, register,\
    authenticate, get_this_user, change_username, change_password, change_icon

from API.Model.userExceptions import not_found_exception, credentials_exception,\
    profile_exception, register_exception, update_exception, update_icon_exception

from API.Model.turnModel import *
from API.Model.gameModel import *

from API.Model.userMetadata import user_metadata


# Add metadata tags for each module
tags_metadata = list(
    chain.from_iterable([
        [{"name": "Root", "description": "", }],
        user_metadata,
    ]
    )
)

app = FastAPI(
    title="Secret Voldemort API",
    description="Secret Voldemort is a multiplayer game based on Secret Hitler where two teams compete against each other for the control of Hogwarts.",
    version="0.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=tags_metadata,
    debug=True
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


@app.get(
    "/",
    tags=["Root"]
)
async def get_root():
    return "Secret Voldemort API"


@app.post(
    USER_REGISTER_URL,
    status_code=status.HTTP_201_CREATED,
    tags=["Register"]
)
async def user_register(new_user: UserRegisterIn):
    try:
        await register(new_user)
    except BaseException:
        raise register_exception
    return {
        "email": new_user.email,
        "result": "success"
    }


@app.post(
    USER_LOGIN_URL,
    status_code=status.HTTP_200_OK,
    tags=["Login"]
)
async def user_login(email: EmailStr = Form(...), password: str = Form(...)):
    return await authenticate(email, password)


@app.get(
    USER_PROFILE_URL,
    status_code=status.HTTP_200_OK,
    tags=["Profile"]
)
async def get_user_public_profile(email: EmailStr):
    try:
        return await get_user_profile_by_email(email)
    except BaseException:
        raise not_found_exception


@app.get(
    USER_ICON_URL,
    status_code=status.HTTP_200_OK,
    tags=["User icon"]
)
async def get_user_icon(email: EmailStr):
    try:
        return Response(await get_user_icon_by_email(email))
    except BaseException:
        raise not_found_exception


@app.put(
    USER_UPDATE_USERNAME_URL,
    status_code=status.HTTP_200_OK,
    tags=["Update username"]
)
async def user_update_username(
        update_data: UserUpdateUsername,
        Authorization: str = Header(...), user: UserProfile = Depends(get_this_user)):
    if update_data.email == user.email and (await change_username(update_data)):
        return {
            "email": update_data.email,
            "result": "success"
        }
    else:
        raise update_exception


@app.put(
    USER_UPDATE_PASSWORD_URL,
    status_code=status.HTTP_200_OK,
    tags=["Update password"]
)
async def user_update_password(
        update_data: UserUpdatePassword,
        Authorization: str = Header(...), user: UserProfile = Depends(get_this_user)):
    if update_data.email == user.email and (await change_password(update_data)):
        return {
            "email": user.email,
            "result": "success"
        }
    else:
        raise update_exception


@app.put(
    USER_UPDATE_ICON_URL,
    status_code=status.HTTP_200_OK,
    tags=["Update icon"]
)
async def user_update_icon(
        email: EmailStr = Form(...), password: str = Form(...), new_icon: UploadFile = File(...),
        Authorization: str = Header(...), user: UserProfile = Depends(get_this_user)):
    update_data = UserUpdateIcon(email=email, password=password)

    if new_icon.content_type not in [
            "image/jpeg", "image/png", "image/bmp", "image/webp"]:
        raise update_icon_exception

    raw_icon = new_icon.file.read()

    if what(new_icon.filename, h=raw_icon) not in [
            "jpeg", "png", "bmp", "webp"]:
        raise update_icon_exception

    if update_data.email == user.email and (await change_icon(update_data, raw_icon)):
        return {
            "email": user.email,
            "result": "success"
        }
    else:
        raise credentials_exception


@app.post("/game/create/",
          status_code=status.HTTP_201_CREATED,
          tags=["Create Game"])
async def create_game(params: GameParams):
    return create_new_game(game_params=params)

# Join Game


@app.put("/game/join/{id}",
         status_code=status.HTTP_200_OK,
         tags=["Join Game"])
async def join_game(id: int, user_email: EmailParameter):
    return join_game_with_keys(game_id=id, user_email=user_email.email)

# Init Game


@app.put("/game/init/{id}",
         status_code=status.HTTP_200_OK,
         tags=["Init Game"])
async def init_game(id: int, player_id: int):
    return init_game_with_ids(game_id=id, player_id=player_id)


# Get list of player ids in the game
@app.get("/game/{id}/players",
         status_code=status.HTTP_200_OK,
         tags=["Players id"]
         )
async def get_player_ids(id: int):
    return check_and_get_player_ids(id)

# Get next player id candidate for minister


@app.put("/game/{id}/select_MM",
         status_code=status.HTTP_200_OK,
         tags=["Next minister candidate"]
         )
async def select_MM(id: int):
    return get_next_MM(id)


# Submit a vote

@app.put("/game/{id}/vote",
         status_code=status.HTTP_200_OK,
         tags=["Submit a vote"]
         )
async def vote(id: int, player_vote: PlayerVote = Body(..., description="Player data: id and vote")):
    return check_and_vote_candidate(id, player_vote.id, player_vote.vote)


# Get the vote result

@app.put("/game/{id}/result",
         status_code=status.HTTP_200_OK,
         tags=["Vote result"]
         )
async def vote_result(id: int):
    return check_and_get_vote_result(id)


# Get three cards

@app.put("/game/{id}/get_cards",
         status_code=status.HTTP_200_OK,
         tags=["Take three cards"]
         )
async def get_cards(id: int):
    return check_and_get_3_cards(id)


# Promulgate a card

@app.put("/game/{id}/promulgate",
         status_code=status.HTTP_200_OK,
         tags=["Promulgate card"]
         )
async def promulgate_card(id: int, promulgate: PlayerPromulgate):
    return promulgate_in_game(
        id, promulgate.candidate_id, promulgate.to_promulgate)


# Check the game status

@app.get("/game/{id}/check_game",
         status_code=status.HTTP_200_OK,
         tags=["Game state"]
         )
async def get_game_status(id: int):
    return game_status(id)
