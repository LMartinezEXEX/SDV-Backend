from pony.orm import *
import datetime


db = Database()
db.bind(provider='sqlite', filename='secretVoldemort.sqlite', create_db=True)

# Declare PonyORM entities before mapping


class User(db.Entity):
    email = PrimaryKey(str, 100)
    username = Required(str, 35, unique=True)
    password = Required(bytes)
    icon = Required(bytes)
    creation_date = Required(datetime.datetime)
    last_access_date = Required(datetime.datetime)
    is_validated = Required(bool)
    refresh_token = Required(str)
    refresh_token_expires = Required(datetime.datetime)
    owner_of = Set('Game')
    playing_in = Set('Player')


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required('User')
    turn = Required(int)
    rol = Optional(str)
    loyalty = Optional(str)
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
    id = PrimaryKey(int, auto=True)
    owner = Required('User')
    name = Required(str, 40)
    min_players = Required(int)
    max_players = Required(int)
    creation_date = Required(datetime.datetime)
    state = Required(int)
    players = Set('Player')
    turn = Set('Turn')
    card = Set('Card')
    board = Optional('Board')


class Turn(db.Entity):
    turn_number = Required(int)
    game = Required('Game')
    current_minister = Required('Player')
    current_director = Required('Player')
    last_minister = Required('Player')
    last_director = Required('Player')
    candidate_minister = Required('Player')
    candidate_director = Required('Player')
    vote = Optional('Vote')
    taken_cards = Required(bool)
    promulgated = Required(bool)
    PrimaryKey(game, turn_number)


class Vote(db.Entity):
    result = Required(bool)
    turn = PrimaryKey('Turn')
    player_vote = Set('Player_vote')


class Player_vote(db.Entity):
    player = Required('Player')
    vote = Required('Vote')
    is_lumos = Required(bool)
    PrimaryKey(vote, player)


class Card(db.Entity):
    order = Required(int, auto=True)
    type = Required(int)
    game = Required('Game')
    PrimaryKey(order, game)


class Board(db.Entity):
    game = PrimaryKey('Game')
    fenix_promulgation = Required(int)
    death_eater_promulgation = Required(int)
    election_counter = Required(int)

#


db.generate_mapping(create_tables=True)
'''
with db_session:

        User(email="lautaro@gmail.br",
             username="pepo",
             password="fachero".encode(),
             icon="".encode(),
             creation_date=datetime.datetime.today(),
             last_access_date=datetime.datetime.today(),
             is_validated=True,
             refresh_token="HolaKappa",
             refresh_token_expires=datetime.datetime.today())

        user = User["lautaro@gmail.br"]

        # Five games instances for test purpose, three 'in game', 1
        # unitiliatlized, 1 finished
        Game(name='LOL',
             owner=user,
             min_players=5,
             max_players=5,
             creation_date=datetime.datetime.today(),
             state=1)

        Game(name='WOW',
             owner=user,
             min_players=5,
             max_players=10,
             creation_date=datetime.datetime.today(),
             state=1)

        # Three players in LOL alives
        game1 = Game[1]

        Board(game=game1,
              fenix_promulgation=0,
              death_eater_promulgation=0,
              election_counter=0)

        Player(turn=1,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game1.id)

        Player(turn=2,
               user=user,
               rol='Fenix',
               loyalty='Fenix',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game1.id)

        Player(turn=3,
               user=user,
               rol='Mortifago',
               loyalty='Mortifago',
               is_alive=True,
               chat_enabled=True,
               is_investigated=False,
               game_in=game1.id)
'''
