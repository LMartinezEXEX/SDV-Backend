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
    chaos = Required(bool)
    players = Set('Player')
    end_game_notified = Optional(IntArray)
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
    pass_cards  = Required(bool)
    reject_notified = Optional(IntArray)
    promulgated = Required(bool)
    imperius_player_id = Required(int)
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
    discarded = Required(bool)
    PrimaryKey(order, game)


class Board(db.Entity):
    game = PrimaryKey('Game')
    fenix_promulgation = Required(int)
    death_eater_promulgation = Required(int)
    election_counter = Required(int)
    spell_available = Required(bool)

#


db.generate_mapping(create_tables=True)
