# Imports
from itertools import chain
from datetime import datetime, timedelta
from typing   import Optional
from pydantic import EmailStr
from fastapi  import FastAPI, Cookie, Response, Depends, Body, File, UploadFile, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.encoders  import jsonable_encoder
from fastapi.security  import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from API.Model.auth    import ACCESS_TOKEN_EXPIRE_MINUTES

# User Model
from API.Model.userModel import UserRegisterIn, UserOperationOut, UserProfile, UserUpdateUsername, UserUpdatePassword, UserUpdateIcon, Token,\
     oauth2_scheme, get_user_by_email, register, authenticate, deauthenticate, new_access_token, get_user_if_active,\
     change_username, change_password, change_icon

from API.Model.userExceptions import register_exception, update_exception

from API.Model.userMetadata import user_metadata, user_metadata_testing

# Turn Model

from API.Model.turnModel import *

# Domain for testing purposes, recommended practice. localtest.me resolves to 127.0.0.1
DOMAIN  = "localtest.me"
EXPIRES = 60 * 60 * 24 * 1000

# Add metadata tags for each module
tags_metadata = list(
    chain.from_iterable([
        [ { "name": "Root", "description": "", } ],
        user_metadata_testing, user_metadata,
        ]
    )
)

app = FastAPI(
    title       = "Secret Voldemort API",
    description = "Secret Voldemort is a multiplayer game based on Secret Hitler where two teams compete against each other for the control of Hogwarts.",
    version     = "0.0.0",
    openapi_url  = "/api/openapi.json",
    docs_url     = "/api/docs",
    redoc_url    = "/api/redoc",
    openapi_tags = tags_metadata
)

# Root
@app.get(
    "/",
    tags = ["Root"]
    )
async def get_root():
    return "Secret Voldemort API"

# Get by email
@app.get(
    "/user/{email}",
    status_code = status.HTTP_200_OK,
    tags = ["User data (Testing)"]
)
async def get_user(email: EmailStr):
    return get_user_by_email(email)

# Register
@app.post(
    "/user/register/",
    response_model = UserOperationOut,
    status_code = status.HTTP_201_CREATED,
    tags = ["Register"]
)
async def user_register(new_user: UserRegisterIn):
    if register(new_user):
        return UserOperationOut(
            username = new_user.username,
            operation_result = "success"
        )
    else:
        raise register_exception

# Login
@app.post(
    "/user/login/",
    status_code = status.HTTP_302_FOUND,
    tags = ["Login"]
)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    # Spec requires the field username, but there we store the email
    email    = form_data.username
    password = form_data.password
    user = authenticate(email, password)

    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = new_access_token(
        data = { "sub": email }, expires_delta = access_token_expires
    )

    access_token_json = jsonable_encoder(access_token)

    response = Response(
        status_code = status.HTTP_302_FOUND,
        headers = {"WWW-Authenticate": "Bearer"}
    )
    response.set_cookie(
            "Authorization",
            value = "Bearer {%s}"%(access_token_json),
            domain= DOMAIN,
            httponly = True,
            max_age = EXPIRES,
            expires = EXPIRES,
    )

    return response

# Logout
@app.post(
    "/user/logout/",
    response_model = UserOperationOut,
    status_code = status.HTTP_302_FOUND,
    tags = ["Logout"]
)
async def user_logout(user: UserProfile = Depends(get_user_if_active)):
    deauthenticate(user.email)
    response = RedirectResponse(url = "/")
    response.delete_cookie("Authorization", domain = DOMAIN)
    return UserOperationOut(
        username = user.username,
        operation_result = "success"
    )

# Profile
@app.get(
    "/user/profile/",
    response_model = UserProfile,
    status_code = status.HTTP_200_OK,
    tags = ["Profile"]
)
async def profile(user: UserProfile = Depends(get_user_if_active)):
    return user

# Update username
@app.put(
    "/user/update/username/",
    status_code = status.HTTP_200_OK,
    tags = ["Update username"]
)
async def user_update(update_data: UserUpdateUsername, user: UserProfile = Depends(get_user_if_active)):
    if update_data.email == user.email and change_username(update_data):
        return UserOperationOut(
            username = user.username,
            operation_result = "success"
        )
    else:
        raise update_exception

# Update password
@app.put(
    "/user/update/password/",
    status_code = status.HTTP_200_OK,
    tags = ["Update password"]
)
async def user_update(update_data: UserUpdatePassword, user: UserProfile = Depends(get_user_if_active)):
    if update_data.email == user.email and change_password(update_data):
        return UserOperationOut(
            username = user.username,
            operation_result = "success"
        )
    else:
        raise update_exception

# Update icon
@app.put(
    "/user/update/icon/",
    status_code = status.HTTP_200_OK,
    tags = ["Update icon"]
)
async def user_update(update_data: UserUpdateIcon, user: UserProfile = Depends(get_user_if_active)):
    if update_data.email == user.email and change_icon(update_data):
        return UserOperationOut(
            username = user.username,
            operation_result = "success"
        )
    else:
        raise update_exception


#-------------------------------------------------------------------------------
#Get next player id candidate for minister
@app.put("/game/{id}/select_MM",
         status_code = status.HTTP_200_OK
         )
async def select_MM(id: int):
    return get_next_MM(id)

# Submit a vote
@app.put("/game/{id}/vote",
        status_code = status.HTTP_200_OK)
async def vote(id: int, player_vote: PlayerVote = Body(..., description="Player data: id and vote")):
    return check_and_vote_candidate(id, player_vote.id, player_vote.vote)

# Get the vote result
@app.put("/game/{id}/result",
        status_code = status.HTTP_200_OK)
async def vote_result(id: int):
    return check_and_get_vote_result(id)

# Get three cards
@app.put("/game/{id}/get_cards",
        status_code = status.HTTP_200_OK)
async def get_cards(id: int):
    return check_and_get_3_cards(id)

# Promulgate a card
@app.put("/game/{id}/promulgate",
        status_code = status.HTTP_200_OK)
async def promulgate_card(id: int, promulgate: PlayerPromulgate):
    return promulgate_in_game(id, promulgate.id, promulgate.to_promulgate)

# Check the game status
@app.get("/game/{id}/check_game",
        status_code = status.HTTP_200_OK)
async def get_game_status(id: int):
    return game_status(id)
