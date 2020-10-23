# Imports
from itertools import chain
from datetime  import datetime, timedelta
from typing    import Optional
from pydantic  import EmailStr
from fastapi   import FastAPI, Cookie, Depends, File, UploadFile, Response, status
from fastapi.responses import RedirectResponse

from fastapi.security  import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from API.Model.auth    import DOMAIN, TOKEN_SEP

# User Model
from API.Model.userModel import UserRegisterIn, UserOperationOut, UserProfile, UserUpdateUsername, UserUpdatePassword, UserUpdateIcon, Token,\
     oauth2_scheme, get_user_profile_by_email, register, authenticate, deauthenticate, new_access_token, get_this_user,\
     change_username, change_password, change_icon

from API.Model.userExceptions import register_exception, update_exception

from API.Model.userMetadata import user_metadata, user_metadata_testing

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
    openapi_tags = tags_metadata,
    debug = True
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
    return get_user_profile_by_email(email)

# Register
@app.post(
    "/user/register/",
    status_code = status.HTTP_201_CREATED,
    tags = ["Register"]
)
async def user_register(new_user: UserRegisterIn):
    try:
        register(new_user)
        return UserOperationOut(
            username = new_user.username, 
            operation_result = "success"
        )
    except Exception as e:
        #raise register_exception
        return str(e)

# Login
@app.post(
    "/user/login/",
    status_code = status.HTTP_302_FOUND,
    tags = ["Login"]
)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Spec requires the field username, but there we store the email
    email    = form_data.username
    password = form_data.password
    return authenticate(email, password)

# Logout
@app.post(
    "/user/logout/",
    status_code = status.HTTP_302_FOUND,
    tags = ["Logout"]
)
async def user_logout(Authorization: str = Cookie(...), user: UserProfile = Depends(get_this_user)):
    authorization_splitted = Authorization.split(TOKEN_SEP)
    if len(authorization_splitted) != 2:
        raise not_authenticated_exception        
    refresh = authorization_splitted[1].strip()
    refresh_splitted = refresh.split(" ")
    if len(refresh_splitted) != 2:
        raise not_authenticated_exception
    refresh_token  = refresh_splitted[1]

    deauthenticate(user.email, refresh_token)
    response = RedirectResponse(url = "/")
    response.delete_cookie("Authorization", domain = DOMAIN)
    return UserOperationOut(
        username = user.username,
        operation_result = "success"
    )

# Profile
@app.get(
    "/user/profile/",
    status_code = status.HTTP_200_OK,
    tags = ["Profile"]
)
async def profile(Authorization: str = Cookie(...), user: UserProfile = Depends(get_this_user)):
    return user

# Update username
@app.put(
    "/user/update/username/",
    status_code = status.HTTP_200_OK,
    tags = ["Update username"]
)
async def user_update(
    update_data: UserUpdateUsername, 
    Authorization: str = Cookie(...), user: UserProfile = Depends(get_this_user)):
    if update_data.email == user.email and change_username(update_data):
        user = get_user_profile_by_email(user.email)
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
async def user_update(
    update_data: UserUpdatePassword, 
    Authorization: str = Cookie(...), user: UserProfile = Depends(get_this_user)):
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
async def user_update(
    email: EmailStr, password: str, new_icon: UploadFile = File(...),
    Authorization: str = Cookie(...), user: UserProfile = Depends(get_this_user)):

    update_data = UserUpdateIcon(email, password)
    
    if new_icon.content_type not in ["image/jpeg", "image/png"]:
        raise update_exception
    if update_data.email == user.email and change_icon(update_data, new_icon):
        return UserOperationOut(
            username = user.username,
            operation_result = "success"
        )
    else:
        raise update_exception
