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

#-------------------------------------------------------------------------------

class Turn(db.Entity):
    turn_number =  PrimaryKey(int, auto=True)
    game = Required('Game')
    current_minister = Required('Player')
    current_director = Required('Player')
    last_minister = Required('Player')
    last_director = Required('Player')
    candidate_minister = Required('Player')
    candidate_director = Required('Player')
    vote = Optional('Vote')
    card = Set('Card')

class Player(db.Entity):
    turn = Required(int, unique=True)
    rol = Required(int)
    loyalty = Required(str)
    is_alive = Required(bool)
    chat_enabled = Required(bool)
    is_investigated = Required(bool)
    current_minister = Set('Turn', reverse='current_minister')
    current_director = Set('Turn', reverse='current_director')
    last_minister = Set('Turn', reverse='last_minister')
    last_director = Set('Turn', reverse='last_director')
    candidate_minister = Set('Turn', reverse='candidate_minister')
    candidate_director = Set('Turn', reverse='candidate_director')
    game_in = Required('Game')
    vote = Set('Player_vote')

class Game(db.Entity):
    name = Required(str, 40)
    min_players = Required(int)
    max_players = Required(int)
    creation_date = Required(datetime.datetime)
    state = Required(int)
    player = Set('Player')
    turn = Set('Turn')
    card = Set('Card')

class Vote(db.Entity):
    result = Required(bool)
    turn = Required('Turn')
    player_vote = Set('Player_vote')

class Player_vote(db.Entity):
    player = Required('Player')
    vote = Required('Vote')
    is_lumos = Required(bool)
    PrimaryKey(vote, player)

class Card(db.Entity):
    order = Required(int, auto=True)
    type = Required(int)
    turn = Required('Turn')
    game = Required('Game')
    PrimaryKey(order, game)
#

db.generate_mapping(create_tables=True)

#-TEST DATA---------------------------------------------------------------------
with db_session:

    Game(name='LOL',
         min_players=5,
         max_players=5,
         creation_date=datetime.datetime.today(),
         state=0)

    game = Game[1]

    Player(turn=1,
           rol=1,
           loyalty='Fenix',
           is_alive=False,
           chat_enabled=True,
           is_investigated=False,
           game_in=game.id)

    Player(turn=2,
           rol=1,
           loyalty='Fenix',
           is_alive=True,
           chat_enabled=True,
           is_investigated=False,
           game_in=game.id)

    Player(turn=3,
           rol=2,
           loyalty='Mortifago',
           is_alive=True,
           chat_enabled=True,
           is_investigated=False,
           game_in=game.id)
