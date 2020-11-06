from pony   import orm
from typing import Optional
from pydantic import EmailStr
from Database.database import User 

from datetime import datetime
import bcrypt

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
    try:
        user = User.get(email = email)
        return bcrypt.checkpw(password.encode(), user.password)
    except:
        return False

@orm.db_session
def last_access(email: EmailStr, last_acces_date: datetime):
    user = User.get(email = email)
    user.last_access_date = last_acces_date

@orm.db_session
def change_username(update_data):
    user = User.get(email = update_data.email)
    user.username = update_data.new_username
    return user.username

@orm.db_session
def change_password(update_data):
    user = User.get(email = update_data.email)
    user.password = bcrypt.hashpw(update_data.new_password.encode(), bcrypt.gensalt(rounds = 6))
    return bcrypt.checkpw(update_data.new_password.encode(), user.password)

@orm.db_session
def change_icon(update_data, new_icon: bytes):
    user = User.get(email = update_data.email)
    user.icon = new_icon
    return user.icon
