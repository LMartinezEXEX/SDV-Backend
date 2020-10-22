# Imports
import re
from typing   import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator
from fastapi  import Depends, Request
from datetime import datetime, timedelta

from API.Model.auth         import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security       import OAuth2, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from jose import JWTError, jwt

from API.Model.userExceptions import credentials_exception, not_authenticated_exception, unauthorized_exception, profile_exception

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
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise not_authenticated_exception
            else:
                return None
        return param

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl = "/user/login/")

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    email: EmailStr
    username: str = Field(min_length = 8, max_length = 20)
    password: str
    icon: bytes   = "".encode()
    creation_date: datetime
    last_access_date: datetime
    is_validated: bool = False
    active: bool       = False
    
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
    active: bool       = False

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
    new_icon: bytes
    password: str

def get_user_by_email(email: EmailStr):
    user = Database.user_functions.get_user_by_email(email)
    if user:
        return UserProfile(
            email    = user.email,
            username = user.username,
            icon     = user.icon,
            active   = user.active,
            is_validated = user.is_validated
        )
    else:
        return UserProfile()

def register(new_user: UserRegisterIn):
    user = User(
        email    = new_user.email,
        username = new_user.username,
        password = new_user.password,
        creation_date    = datetime.now(),
        last_access_date = datetime.now()
    )
    
    try:
        Database.user_functions.register_user(user)
        return True
    except:
        return False

def get_user_auth(email: EmailStr) -> Dict[str, Any]:
    user = Database.user_functions.get_user_by_email(email)
    if user:
        return UserProfile(
            email    = user.email,
            username = user.username,
            icon     = user.icon,
            active   = user.active,
            is_validated = user.is_validated
        )
    else:
        return UserProfile()

def authenticate(email: EmailStr, password: str) -> Dict[str, Any]:
    if Database.user_functions.auth_user_password(email, password):
        if not Database.user_functions.is_active_user(email):
            Database.user_functions.switch_state_active_user(email)
            return get_user_auth(email)
        else:
            raise credentials_exception
    else:
        raise unauthorized_exception

def deauthenticate(email: EmailStr):
    if Database.user_functions.is_active_user(email):
        Database.user_functions.switch_state_deactive_user(email)
        return get_user_auth(email)
    else:
        raise credentials_exception

def new_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({ "exp": expire })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

async def get_this_user(token: str = Depends(oauth2_scheme)):
    try:
        # Clear '{' and '}' from token
        token = re.sub("^{|}$", "", token)

        payload     = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        token_email = payload.get("sub")

        if token_email is None:
            raise credentials_exception

        user = get_user_auth(email = token_email)

        if user is None:
            raise credentials_exception
        
        return user
    except JWTError:
        raise credentials_exception

async def get_user_if_active(user: UserProfile = Depends(get_this_user)):
    if not user.active:
        raise profile_exception
    return user

def change_username(update_data: UserUpdateUsername) -> bool:
    return update_data.new_username == Database.user_functions.change_username(update_data)

def change_password(update_data: UserUpdatePassword) -> bool:
    if update_data.old_password == update_data.new_password:
        return False
    return Database.user_functions.change_password(update_data)

def change_icon(update_data: UserUpdateIcon) -> bool:
    return update_data.new_icon == Database.user_functions.change_icon(update_data)
