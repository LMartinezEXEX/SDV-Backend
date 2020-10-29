from pony.orm import *
import datetime


db = Database()
db.bind(provider='sqlite', filename='secretVoldemort.sqlite', create_db=True)

# Agregar entidades antes del mapping


class User(db.Entity):
    email = PrimaryKey(str, 100)
    username = Required(str, 20, unique=True)
    password = Required(str)
    icon = Optional(bytes, nullable=True)
    creation_date = Required(datetime.date)
    last_access_date = Required(datetime.date)
    is_validated = Required(bool)
    active = Required(bool)
    owner_of = Set('Game')
    playing_in = Set('Player')


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    owner = Required('User')
    name = Required(str, 40)
    creation_date = Required(datetime.date)
    state = Required(int)
    min_players = Required(int)
    max_players = Required(int)
    players = Set('Player')
    board = Optional('Board')


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required('User')
    is_alive = Required(bool)
    game = Required('Game')
    rol = Optional(str)
    loyalty = Optional(str)
    chat_enabled = Required(bool)
    investigated = Required(bool)


class Board(db.Entity):
    game = PrimaryKey('Game')
    fenix_promulgation = Required(int)
    death_eater_promulgation = Required(int)
    election_counter = Required(int)


#


db.generate_mapping(create_tables=True)
