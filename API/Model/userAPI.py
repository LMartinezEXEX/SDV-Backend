import json
from secrets import token_hex
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr, validator
from fastapi import Cookie, Header, Depends, Request, Response, status
from fastapi.encoders import jsonable_encoder
from jose import JWTError, ExpiredSignatureError, jwt
from API.Model.exceptions import *
from API.Model.token_data import *
from USER_URLS import USER_LOGIN_URL
from API.Model.security_scheme import OAuth2PasswordBearer
from API.Model.models import *
from Database.user_functions import *


# Actual security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=USER_LOGIN_URL)

async def get_user_profile_by_email(email: EmailStr):
    user = get_user_by_email(email)
    return UserProfile(
        email=user.email,
        username=user.username,
        last_access_date=user.last_access_date,
        is_validated=user.is_validated
    )


async def get_user_icon_by_email(email: EmailStr):
    user = get_user_by_email(email)
    return user.icon


async def register(new_user: UserRegisterIn):
    register_user(
        User(
            email=new_user.email,
            username=new_user.username,
            password=new_user.password,
            icon="".encode(),
            creation_date=datetime.utcnow(),
            last_access_date=datetime.utcnow(),
            is_validated=False
        )
    )


async def is_valid_user(email: EmailStr):
    user = await get_user_profile_by_email(email)
    return user.is_validated


async def authenticate(email: EmailStr, password: str):
    if auth_user_password(email, password):
        user = await get_user_profile_by_email(email)
        access_token = await new_access_token(
            data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        )
        access_token_json = jsonable_encoder(access_token)

        last_access_date = datetime.utcnow()

        last_access(
            user.email,
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
        raise credentials_exception


async def new_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_this_user(
    request: Request,
    Authorization: str = Header(...),
    access_token = Depends(oauth2_scheme)):
    try:
        # This is the case of user being logged and checks are fine,ie no
        # exceptions
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        token_email = payload.get("sub")

        if token_email is None:
            raise credentials_exception
        user = await get_user_profile_by_email(token_email)
        if user is None:
            raise credentials_exception

        return user
    except JWTError:
        # Any other exception
        raise credentials_exception


async def change_username(update_data: UserUpdateUsername):
    if auth_user_password(
            update_data.email, update_data.password):
        return update_data.new_username == change_username(
            update_data)
    else:
        return False


async def change_password(update_data: UserUpdatePassword):
    if update_data.old_password != update_data.new_password and auth_user_password(
            update_data.email, update_data.old_password):
        return change_password(update_data)
    return False


async def change_icon(update_data: UserUpdateIcon, new_icon: bytes):
    if auth_user_password(
            update_data.email, update_data.password):
        return new_icon == change_icon(
            update_data, new_icon)
    else:
        return False
