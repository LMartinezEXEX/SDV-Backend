# Imports
from secrets  import token_hex
from typing   import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr, validator
from fastapi  import Cookie, Depends, Request, Response, status
from fastapi.encoders       import jsonable_encoder
from fastapi.security       import OAuth2, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from jose import JWTError, ExpiredSignatureError, jwt

from API.Model.userExceptions import credentials_exception, not_authenticated_exception, unauthorized_exception, profile_exception
from API.Model.auth import SECRET_KEY, ALGORITHM, TOKEN_SEP, DOMAIN, ACCESS_TOKEN_EXPIRES_MINUTES, REFRESH_TOKEN_EXPIRES_MINUTES, EXPIRES_REFRESH, REFRESH_TOKEN_LENGTH

# Database
import Database.user_functions

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict     = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password = {"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows = flows, scheme_name = scheme_name, auto_error = auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        cookie_authorization: str = request.cookies.get("Authorization")

        authorization_splitted = cookie_authorization.split(TOKEN_SEP)
        if len(authorization_splitted) != 2:
            raise not_authenticated_exception
        
        bearer  = authorization_splitted[0].strip()
        refresh = authorization_splitted[1].strip()

        refresh_splitted = refresh.split(" ")
        if len(refresh_splitted) != 2:
            raise not_authenticated_exception

        refresh_scheme = refresh_splitted[0]
        refresh_token  = refresh_splitted[1]

        cookie_scheme, cookie_token = get_authorization_scheme_param(
            bearer
        )

        if cookie_scheme.lower() == "bearer" and refresh_scheme.lower() == "refresh":
            authorization = True
            scheme = cookie_scheme
            token  = cookie_token

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer" or refresh_scheme.lower() != "refresh":
            if self.auto_error:
                raise not_authenticated_exception
            else:
                return None
        
        return cookie_token, refresh_token

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl = "/user/login/")

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    email: EmailStr
    username: str = Field(min_length = 8, max_length = 35)
    password: str = Field(min_length = 8, max_length = 50)
    icon: bytes
    creation_date: datetime
    last_access_date: datetime
    is_validated: bool
    refresh_token: str
    refresh_token_expires: datetime
    
    @validator("email")
    def email_size(cls, val):
        if len(val) > 100:
            raise ValueError("Length of email is greater than 100")
        return val
    
    class Config:
        orm_mode = True

class UserRegisterIn(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserOperationOut(BaseModel):
    username: str
    operation_result: str

class UserProfile(BaseModel):
    email: EmailStr = ""
    username: str   = ""
    icon: bytes     = "".encode()
    is_validated: bool = False

class UserProfileExtended(UserProfile):
    refresh_token: str = ""
    refresh_token_expires: datetime = None

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

def get_user_profile_by_email(email: EmailStr):
    user = Database.user_functions.get_user_by_email(email)
    if user:
        return UserProfile(
            email    = user.email,
            username = user.username,
            icon     = user.icon,
            is_validated = user.is_validated
        )
    else:
        return UserProfile()

def register(new_user: UserRegisterIn):
    user = User(
        email    = new_user.email,
        username = new_user.username,
        password = new_user.password,
        icon     = "".encode(),
        creation_date    = datetime.now(),
        last_access_date = datetime.now(),
        is_validated  = False,
        refresh_token = "empty",
        refresh_token_expires = datetime(year = 1970, month = 1, day = 1, hour = 0, minute = 0, second = 0, microsecond = 0)
    )
    Database.user_functions.register_user(user)

def get_user_auth(email: EmailStr):
    user = Database.user_functions.get_user_by_email(email)
    if user:
        return UserProfileExtended(
            email    = user.email,
            username = user.username,
            icon     = user.icon,
            is_validated  = user.is_validated,
            refresh_token = user.refresh_token,
            refresh_token_expires = user.refresh_token_expires
        )
    else:
        return UserProfileExtended()

def authenticate(email: EmailStr, password: str):
    if Database.user_functions.auth_user_password(email, password):
        user = get_user_auth(email)
        if user.refresh_token == "empty":
            access_token = new_access_token(
                data = { "sub": email }, expires_delta = timedelta(minutes = ACCESS_TOKEN_EXPIRES_MINUTES)
            )
            access_token_json = jsonable_encoder(access_token)

            refresh_token_value = token_hex(REFRESH_TOKEN_LENGTH)
            refresh_token_expires = datetime.utcnow() + timedelta(minutes = REFRESH_TOKEN_EXPIRES_MINUTES)

            Database.user_functions.activate_user(email, refresh_token_value, refresh_token_expires)
            
            response = Response(
                status_code = status.HTTP_302_FOUND,
                headers = {"WWW-Authenticate": "Bearer"}
            )
            response.set_cookie(
                key = "Authorization",
                value    = f"Bearer {access_token_json} {TOKEN_SEP} Refresh {refresh_token_value}",
                domain   = DOMAIN,
                httponly = True,
                max_age  = EXPIRES_REFRESH,
                expires  = EXPIRES_REFRESH,
            )

            return response
        else:
            raise credentials_exception
    else:
        raise unauthorized_exception

def deauthenticate(email: EmailStr, refresh_token: str):
    user = get_user_auth(email)
    # Logout user by request if refresh token is the same
    if user.refresh_token != "empty" and user.refresh_token == refresh_token:
        Database.user_functions.deactivate_user(email)
    else:
        raise not_authenticated_exception

def new_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({ "exp": expire })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

async def get_this_user(tokens: Tuple[str, str] = Depends(oauth2_scheme)):
    access_token  = tokens[0]
    refresh_token = tokens[1]
    try:
        # This is the case of user being logged and checks are fine
        payload     = jwt.decode(access_token, SECRET_KEY, algorithms = [ALGORITHM])
        token_email = payload.get("sub")
        if token_email is None:
            raise credentials_exception
        user = get_user_auth(email = token_email)
        if user is None:
            raise credentials_exception
        if user.refresh_token == "empty" or user.refresh_token != refresh_token:
            raise profile_exception
        return UserProfile(
            email    = user.email,
            username = user.username,
            icon     = user.icon,
            is_validated = user.is_validated
        )
    except ExpiredSignatureError:
        # This is the case where signature expired
        # Signature expired, but we need to know if refresh expired too
        payload = jwt.decode(access_token, SECRET_KEY, algorithms = [ALGORITHM], options = { "verify_exp": False })
        token_email = payload.get("sub")
        expires     = payload.get("exp")

        if token_email is None:
            raise credentials_exception
        user = get_user_auth(email = token_email)
        if user is None:
            raise credentials_exception
        
        if user.refresh_token != "empty" and user.refresh_token == refresh_token and user.refresh_token_expires < datetime.utcnow():
                # Refresh token corresponds to user and
                # Bearer token expired but Refresh token didn't, so issue new tokens
                access_token = new_access_token(
                    data = { "sub": user.email }, expires_delta = timedelta(minutes = ACCESS_TOKEN_EXPIRES_MINUTES)
                )
                access_token_json = jsonable_encoder(access_token)
                refresh_token_value = token_hex(REFRESH_TOKEN_LENGTH)
                refresh_token_expires = datetime.utcnow() + timedelta(minutes = REFRESH_TOKEN_EXPIRES_MINUTES)
                Database.user_functions.activate_user(email, refresh_token_value, refresh_token_expires)
                response = Response(
                    status_code = status.HTTP_302_FOUND,
                    headers = {"WWW-Authenticate": "Bearer"}
                )
                response.set_cookie(
                    key = "Authorization",
                    value    = f"Bearer {access_token_json} {TOKEN_SEP} Refresh {refresh_token_value}",
                    domain   = DOMAIN,
                    httponly = True,
                    max_age  = EXPIRES_REFRESH,
                    expires  = EXPIRES_REFRESH,
                )
                response.content = get_user_profile_by_email(user.email)
                return user
        else:
            # Refresh token is not tracked, then token is being replayed somehow
            # Or Refresh token is not equal to the stored one
            # Or Refresh token expired
            Database.user_functions.deactivate_user(user.email)
            raise profile_exception
    except JWTError:
        # Any other exception
        raise credentials_exception

def change_username(update_data: UserUpdateUsername) -> bool:
    return update_data.new_username == Database.user_functions.change_username(update_data)

def change_password(update_data: UserUpdatePassword) -> bool:
    if update_data.old_password == update_data.new_password:
        return False
    return Database.user_functions.change_password(update_data)

def change_icon(update_data: UserUpdateIcon, new_icon: bytes) -> bool:
    return new_icon == Database.user_functions.change_icon(update_data, new_icon)
