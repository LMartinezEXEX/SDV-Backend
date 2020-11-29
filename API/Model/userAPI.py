import os
from random import randrange, seed
from datetime import datetime, timedelta
from pydantic import EmailStr
from fastapi import Header, Depends, UploadFile, Response, status
from fastapi.encoders import jsonable_encoder
from typing import Dict, Any, Optional, Tuple
from jose import JWTError, ExpiredSignatureError, jwt
from pydantic import BaseModel, Field, EmailStr, validator
from fastapi import Cookie, Header, Depends, Request, Response, status
from API.Model.models import *
from API.Model.exceptions import *
from API.Model.token_data import *
import Database.user_functions as db_user
from API.Model.security_scheme import OAuth2PasswordBearer
import API.Model.user_check as user_check
from URLS import *

ASSETS_BASE_DIR = "Assets"
ICONS_DIR = "icons"
DEFAULT_ICONS = [
    "draco.jpg", "harry.jpg", "hermione.jpg", "lucius.jpg", "ron.jpg",
    "snape.jpg", "umbridge.jpg", "voldemort.jpg"
]


# Actual security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=USER_LOGIN_URL)


async def get_user_profile_by_email(email: EmailStr):
    try:
        user = db_user.get_user_by_email(email)
        return UserProfile(
            email=user.email,
            username=user.username,
            last_access_date=user.last_access_date,
            is_validated=user.is_validated
        )
    except:
        raise user_not_found_exception


async def get_user_icon_by_email(email: EmailStr):
    try:
        user = db_user.get_user_by_email(email)
        return user.icon
    except:
        raise user_not_found_exception


async def register(new_user: UserRegisterIn):
    seed()
    icon_file = DEFAULT_ICONS[randrange(len(DEFAULT_ICONS))]
    path_icon_file = os.path.realpath(
        os.path.join(os.path.dirname(__file__), "..", "..", ASSETS_BASE_DIR, ICONS_DIR, icon_file)
    )
    random_icon = None
    try:
        icon_file = open(path_icon_file, "rb")
        random_icon = icon_file.read()
    except:
        raise asset_file_icon_exception
    else:
        try:
            db_user.register_user(
                User(
                    email=new_user.email,
                    username=new_user.username,
                    password=new_user.password,
                    icon=random_icon,
                    creation_date=datetime.utcnow(),
                    last_access_date=datetime.utcnow(),
                    is_validated=False
                )
            )
        except Exception as e:
            raise e
        finally:
            icon_file.close()


async def is_valid_user(email: EmailStr):
    user = await get_user_profile_by_email(email)
    return user.is_validated


async def authenticate(email: EmailStr, password: str):
    if db_user.auth_user_password(email, password):
        access_token = await new_access_token(
            data={"sub": email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        )
        access_token_json = jsonable_encoder(access_token)
        last_access_date = datetime.utcnow()
        db_user.last_access(
            email,
            last_access_date)
        response = Response(
            status_code=status.HTTP_200_OK,
            headers={
                "WWW-Authenticate": "Bearer",
                "Authorization": f"Bearer {access_token_json}"
            }
        )
        return response
    else:
        raise incorrect_password_exception


async def new_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_this_user(Authorization: str = Header(...), access_token = Depends(oauth2_scheme)):
    try:
        # This is the case of user being logged and checks are fine, ie no
        # exceptions
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        token_email = payload.get("sub")

        if token_email is None:
            raise credentials_exception

        return await get_user_profile_by_email(token_email)
    except ExpiredSignatureError:
        raise expired_signature_exception
    except JWTError:
        # Any other exception
        raise invalid_token_exception
    except Exception as e:
        raise e


async def change_username(update_data: UserUpdateUsername):
    authenticated = db_user.auth_user_password(update_data.email, update_data.password)
    if authenticated:
        db_user.change_username(update_data.email, update_data.new_username)
    return authenticated


async def change_password(update_data: UserUpdatePassword):
    authenticated = db_user.auth_user_password(update_data.email, update_data.old_password)
    if authenticated:
        db_user.change_password(update_data.email, update_data.new_password)
    return authenticated


async def change_icon(update_data: UserUpdateIcon, new_icon: UploadFile):
    authenticated = db_user.auth_user_password(update_data.email, update_data.password)
    if authenticated:
        try:
            raw_icon = user_check.icon_validate(new_icon)
            db_user.change_icon(update_data.email, raw_icon)
        except Exception as e:
            raise e
    return authenticated
