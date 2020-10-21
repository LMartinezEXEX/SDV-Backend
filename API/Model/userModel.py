# Imports
from typing   import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator
from fastapi  import Depends, HTTPException
from datetime import datetime, timedelta

# Security
from API.Model.auth   import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

# Database
import Database.user_functions

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/user/login/")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

class User(BaseModel):
    email: EmailStr
    username: str = Field(min_length = 8, max_length = 20)
    password: bytes
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

class UserRegisterOut(BaseModel):
    username: str
    operation_result: str

class UserLoginData(BaseModel):
    email: EmailStr
    username: str
    password: bytes
    active: bool

def get_user_by_email(email: EmailStr) -> Dict[str, Any]:
    user = None
    user = Database.user_functions.get_user_by_email(email)
    if not user:
        return {}
    else:
        return {
            "email": user.email,
            "username": user.username,
            "icon": user.icon,
            "is_validated": user.is_validated
        }

def register(new_user: UserRegisterIn) -> Dict[str, Any]:
    user = User(
        email    = new_user.email,
        username = new_user.username,
        password = new_user.password.encode(),
        creation_date    = datetime.now(),
        last_access_date = datetime.now()
    )
    
    try:
        Database.user_functions.register_user(user)
        return { "message": "Ok", "created": True }
    except Exception as e:
        return { "message": str(e), "created": False }


def get_user_auth(email: EmailStr) -> Dict[str, Any]:
    user = Database.user_functions.get_user_by_email(email)
    return {
        "email": user.email,
        "username": user.username,
        "password": user.password,
        "active": user.active
    }

def authenticate(email: EmailStr, password: str) -> Dict[str, Any]:
    data_user = None
    if Database.user_functions.auth_user(email, password.encode()):
        user = Database.user_functions.get_user_by_email(email)
        data_user = {
            "email": user.email,
            "username": user.username,
            "password": user.password,
            "active": user.active
        }
    return data_user

def new_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = 15)
    to_encode.update({ "exp": expire })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

async def get_this_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail      = "Could not validate credentials",
        headers     = { "WWW-Authenticate": "Bearer" },
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email = email)
    except JWTError:
        raise credentials_exception
    
    user = get_user_auth(email = token_data.email)

    if user is None:
        raise credentials_exception
    return user

async def get_user_if_active(user: UserLoginData = Depends(get_this_user)):
    if not user.active:
        raise HTTPException(status_code = 400, detail = "Inactive user")
    return user

def change_username(email: EmailStr, new_username: str) -> bool:
    return new_username == Database.user_functions.change_username(email, new_username)

def change_password(email: EmailStr, old_password: str, new_password: str) -> bool:
    if old_password == new_password:
        return False
    return Database.user_functions.change_password(email, old_password.encode(), new_password.encode())

def change_icon(email: EmailStr, new_icon: bytes) -> bool:
    return new_icon == Database.user_functions.change_icon(email, new_icon)
