from pony.orm import *

import datetime

db = Database()
db.bind(provider='sqlite', filename='secretVoldemort.sqlite', create_db=True)

# Agregar entidades antes del mapping

# User

class User(db.Entity):
    email    = PrimaryKey(str, 100)
    username = Required(str, 20, unique = True)
    password = Required(bytes)
    icon     = Required(bytes)
    creation_date    = Required(datetime.datetime)
    last_access_date = Required(datetime.datetime)
    is_validated     = Required(bool)
    active           = Required(bool)

#

db.generate_mapping(create_tables=True)
