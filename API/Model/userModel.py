# Imports
import json
from secrets import token_hex
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from pydantic import BaseModel, Field, EmailStr, validator
from fastapi import Cookie, Header, Depends, Request, Response, status
from fastapi.encoders import jsonable_encoder
from jose import JWTError, ExpiredSignatureError, jwt

# Exceptions
from API.Model.userExceptions import credentials_exception, not_authenticated_exception, \
    unauthorized_exception, not_found_exception
# Data for user management
from API.Model.authData import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRES_MINUTES
from USER_URLS import USER_LOGIN_URL
# Security scheme
from API.Model.securityScheme import OAuth2PasswordBearerWithCookie
# Database

import Database.user_functions


# Actual security scheme
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl=USER_LOGIN_URL)

# User models


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


async def get_user_profile_by_email(email: EmailStr):
    user = Database.user_functions.get_user_by_email(email)
    return UserProfile(
        email=user.email,
        username=user.username,
        last_access_date=user.last_access_date,
        is_validated=user.is_validated
    )


async def get_user_icon_by_email(email: EmailStr):
    user = Database.user_functions.get_user_by_email(email)
    return user.icon


async def register(new_user: UserRegisterIn):
    Database.user_functions.register_user(
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
    if Database.user_functions.auth_user_password(email, password):
        user = await get_user_profile_by_email(email)
        access_token = await new_access_token(
            data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        )
        access_token_json = jsonable_encoder(access_token)

        last_access_date = datetime.utcnow()

        Database.user_functions.last_access(
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


async def new_access_token(data: dict, expires_delta: Optional[timedelta] = None):
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
    if Database.user_functions.auth_user_password(
            update_data.email, update_data.password):
        return update_data.new_username == Database.user_functions.change_username(
            update_data)
    else:
        return False


async def change_password(update_data: UserUpdatePassword):
    if update_data.old_password != update_data.new_password and Database.user_functions.auth_user_password(
            update_data.email, update_data.old_password):
        return Database.user_functions.change_password(update_data)
    return False


async def change_icon(update_data: UserUpdateIcon, new_icon: bytes):
    if Database.user_functions.auth_user_password(
            update_data.email, update_data.password):
        return new_icon == Database.user_functions.change_icon(
            update_data, new_icon)
    else:
        return False
