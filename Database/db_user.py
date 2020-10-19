import datetime


def create_user_entity(db, orm):
    class User(db.Entity):
        email = orm.PrimaryKey(str, 100)
        name = orm.Required(str, 20, unique=True)
        password = orm.Required(str, 35)
        creation_date = orm.Required(datetime.datetime)
        last_access_date = orm.Required(datetime.datetime)
        is_validated = orm.Required(bool)

    return User
