import bcrypt
from pony import orm
from typing import Optional
from pydantic import EmailStr
from datetime import datetime
from Database.database import *


@orm.db_session
def get_user_by_email(email: EmailStr):
    return User.get(email = email)


@orm.db_session
def register_user(new_user):
    User(
        email    = new_user.email,
        username = new_user.username,
        password = bcrypt.hashpw(new_user.password.encode(), bcrypt.gensalt(rounds = 6)),
        icon     = new_user.icon,
        creation_date    = new_user.creation_date,
        last_access_date = new_user.last_access_date,
        is_validated     = new_user.is_validated
    )


@orm.db_session
def auth_user_password(email: EmailStr, password: str):
    user = User.get(email = email)
    
    return bcrypt.checkpw(password.encode(), user.password)


@orm.db_session
def last_access(email: EmailStr, last_acces_date: datetime):
    user = User.get(email = email)
    user.last_access_date = last_acces_date


@orm.db_session
def change_username(email: EmailStr, new_username: str):
    user = User.get(email = email)
    user.username = new_username


@orm.db_session
def change_password(email: EmailStr, new_password: str):
    user = User.get(email = email)
    user.password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds = 6))


@orm.db_session
def change_icon(email: EmailStr, new_icon: bytes):
    user = User.get(email = email)
    user.icon = new_icon
