from pony import orm
import API.Model.userModel
import datetime
import bcrypt

db = orm.Database()

class User(db.Entity):
    email    = orm.PrimaryKey(str, 100)
    username = orm.Required(str, 20, unique = True)
    password = orm.Required(bytes)
    icon     = orm.Required(bytes)
    creation_date    = orm.Required(datetime.datetime)
    last_access_date = orm.Required(datetime.datetime)
    is_validated     = orm.Required(bool)
    active           = orm.Required(bool)

# sqlite de forma provisional
# En este caso gaurdamos os users en un archivo distinto
db.bind(provider = 'sqlite', filename = 'users.sqlite', create_db = True)
db.generate_mapping(create_tables = True)

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
def auth_user(email: str, password: bytes) -> bool:
    user = User.get(email = email)
    return bcrypt.checkpw(password, user.password)

@orm.db_session
def change_username(email: str, new_username: str) -> str:
    user = User.get(email = email)
    user.username = new_username
    return user.username

@orm.db_session
def change_password(email: str, old_password: bytes, new_password: bytes):
    user = User.get(email = email)
    if bcrypt.checkpw(old_password, user.password):
        user.password = bcrypt.hashpw(new_password, bcrypt.gensalt(rounds = 6))
    return bcrypt.checkpw(new_password, user.password)

@orm.db_session
def change_icon(email: str, new_icon: bytes):
    user = User.get(email = email)
    user.icon = new_icon
    return user.icon
