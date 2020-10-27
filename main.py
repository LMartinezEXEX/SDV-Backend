# Imports
import json
from imghdr       import what
from itertools    import chain
from datetime     import datetime, timedelta
from typing       import Optional
from http.cookies import SimpleCookie
from pydantic     import EmailStr
from fastapi      import FastAPI, Cookie, Depends, Form, File, UploadFile, Response, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security   import OAuth2PasswordRequestForm
from API.Model.authData import DOMAIN, TOKEN_SEP
from USER_URLS import USER_REGISTER_URL, USER_LOGIN_URL, USER_LOGOUT_URL, USER_PUBLIC_PROFILE_URL,\
     USER_PRIVATE_PROFILE_URL, USER_ICON_URL, USER_UPDATE_USERNAME_URL, USER_UPDATE_PASSWORD_URL, USER_UPDATE_ICON_URL

# User Model
from API.Model.userModel import UserRegisterIn, UserProfileExtended,\
     UserUpdateUsername, UserUpdatePassword, UserUpdateIcon,\
     get_user_profile_by_email, get_user_icon_by_email, register,\
     authenticate, deauthenticate, get_this_user,\
     change_username, change_password, change_icon

from API.Model.userExceptions import not_found_exception, credentials_exception,\
     profile_exception, register_exception, update_exception, update_icon_exception

from API.Model.userMetadata import user_metadata

# Add metadata tags for each module
tags_metadata = list(
    chain.from_iterable([
        [ { "name": "Root", "description": "", } ],
        user_metadata,
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
    openapi_tags = tags_metadata,
    debug = True
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Root
@app.get(
    "/",
    tags = ["Root"]
    )
async def get_root():
    return "Secret Voldemort API"

# Register
@app.post(
    USER_REGISTER_URL,
    status_code = status.HTTP_201_CREATED,
    tags = ["Register"]
)
async def user_register(new_user: UserRegisterIn):
    try:
        await register(new_user)
    except:
        raise register_exception
    return {
        "username": new_user.username,
        "operation_result": "success"
    }

# Login
@app.post(
    USER_LOGIN_URL,
    status_code = status.HTTP_302_FOUND,
    tags = ["Login"]
)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Spec requires the field username, but there we store the email
    email    = form_data.username
    password = form_data.password
    return await authenticate(email, password)

# Get public profile by email
@app.get(
    USER_PUBLIC_PROFILE_URL,
    status_code = status.HTTP_200_OK,
    tags = ["User public data"]
)
async def get_user_public_profile(email: EmailStr):
    try:
        return await get_user_profile_by_email(email)
    except:
        raise not_found_exception

# Get icon by email
@app.get(
    USER_ICON_URL,
    status_code = status.HTTP_200_OK,
    tags = ["User icon"]
)
async def get_user_icon(email: EmailStr):
    try:
        return Response(await get_user_icon_by_email(email))
    except:
        raise not_found_exception

# Profile
@app.get(
    USER_PRIVATE_PROFILE_URL,
    status_code = status.HTTP_200_OK,
    tags = ["Private profile"]
)
async def profile(Authorization: str = Cookie(...), response: Response = Depends(get_this_user)):
    return response

# Logout
@app.post(
    USER_LOGOUT_URL,
    status_code = status.HTTP_302_FOUND,
    tags = ["Logout"]
)
async def user_logout(Authorization: str = Cookie(...), response: Response = Depends(get_this_user)):
    user = UserProfileExtended(**json.loads(response.body.decode()))
    authorization_splitted = Authorization.split(TOKEN_SEP)
    if len(authorization_splitted) != 2:
        raise not_authenticated_exception
    refresh = authorization_splitted[1].strip()
    refresh_splitted = refresh.split(" ")
    if len(refresh_splitted) != 2:
        raise not_authenticated_exception
    refresh_token  = refresh_splitted[1]
    await deauthenticate(user.email, refresh_token)
    response = Response(
        content = json.dumps({
            "username": user.username,
            "operation_result": "success"
        }).encode(),
        status_code = status.HTTP_302_FOUND,
        headers = { "Location": DOMAIN + "/" }
    )
    response.delete_cookie("Authorization", domain = DOMAIN)
    return response

# Update username
@app.put(
    USER_UPDATE_USERNAME_URL,
    status_code = status.HTTP_200_OK,
    tags = ["Update username"]
)
async def user_update_username(
    update_data: UserUpdateUsername, 
    Authorization: str = Cookie(...), response: Response = Depends(get_this_user)):
    user = UserProfileExtended(**json.loads(response.body.decode()))
    if update_data.email == user.email and (await change_username(update_data)):
        response.body = json.dumps({
            "username": update_data.new_username,
            "operation_result": "success"
        }).encode()
        return response
    else:
        raise update_exception

# Update password
@app.put(
    USER_UPDATE_PASSWORD_URL,
    status_code = status.HTTP_200_OK,
    tags = ["Update password"]
)
async def user_update_password(
    update_data: UserUpdatePassword, 
    Authorization: str = Cookie(...), response: Response = Depends(get_this_user)):
    user = UserProfileExtended(**json.loads(response.body.decode()))
    if update_data.email == user.email and (await change_password(update_data)):
        response.body = json.dumps({
            "username": user.username,
            "operation_result": "success"
        }).encode()
        return response
    else:
        raise update_exception

# Update icon
@app.put(
    USER_UPDATE_ICON_URL,
    status_code = status.HTTP_200_OK,
    tags = ["Update icon"]
)
async def user_update_icon(
    email: EmailStr = Form(...), password: str = Form(...), new_icon: UploadFile = File(...),
    Authorization: str = Cookie(...), response: Response = Depends(get_this_user)):
    user = UserProfileExtended(**json.loads(response.body.decode()))
    update_data = UserUpdateIcon(email = email, password = password)

    if new_icon.content_type not in ["image/jpeg", "image/png", "image/bmp", "image/webp"]:
        raise update_icon_exception

    raw_icon = new_icon.file.read()

    if what(new_icon.filename ,h = raw_icon) not in ["jpeg", "png", "bmp", "webp"]:
        raise update_icon_exception
    
    if update_data.email == user.email and (await change_icon(update_data, raw_icon)):
        response.body = json.dumps({
            "username": user.username,
            "operation_result": "success"
        }).encode()
        return response
    else:
        raise credentials_exception
