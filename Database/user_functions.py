from pony import orm
from Database.database import User

import datetime
import bcrypt

@orm.db_session
def get_user_by_email(email: str):
    return User.get(email = email)

@orm.db_session
def register_user(new_user: User):
    User(
        email    = new_user.email,
        username = new_user.username,
        password = bcrypt.hashpw(new_user.password, bcrypt.gensalt(rounds = 6)),
        icon     = new_user.icon,
        creation_date    = new_user.creation_date,
        last_access_date = new_user.last_access_date,
        is_validated     = new_user.is_validated,
        active           = new_user.active
    )

@orm.db_session
def auth_user_password(email: str, password: str) -> bool:
    try:
        user = User.get(email = email)
        return bcrypt.checkpw(password.encode(), user.password)
    except:
        return False

@orm.db_session
def is_active_user(email: str) -> bool:
    user = User.get(email = email)
    return user.active

@orm.db_session
def switch_state_active_user(email: str) -> bool:
    user = User.get(email = email)
    user.active = True

@orm.db_session
def switch_state_deactive_user(email: str) -> bool:
    user = User.get(email = email)
    user.active = False

@orm.db_session
def change_username(update_data):
    if auth_user_password(update_data.email, update_data.password):
        user = User.get(email = update_data.email)
        user.username = update_data.new_username
        return user.username

@orm.db_session
def change_password(update_data):
    if auth_user_password(update_data.email, update_data.old_password):
        user = User.get(email = update_data.email)
        user.password = bcrypt.hashpw(update_data.new_password.encode(), bcrypt.gensalt(rounds = 6))
        return bcrypt.checkpw(update_data.new_password.encode(), user.password)

@orm.db_session
def change_icon(update_data):
    if auth_user_password(update_data.email, update_data.old_password):
        user = User.get(email = update_data.email)
        user.icon = update_data.new_icon
        return user.icon
