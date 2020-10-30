from datetime import datetime
from pony.orm import *
from Database.database import Player, User, Game, Board, db
from pydantic import EmailStr
from fastapi import HTTPException, status
from API.Model.gameExceptions import *


@db_session
def get_user_by_email(email: EmailStr):
    return User.get(email=email)


@db_session
def get_game_by_id(game_id: int):
    return Game.get(id=game_id)


@db_session
def get_player_by_id(player_id: int):
    return Player.get(id=player_id)


@db_session
def is_player_in_game(user_email: EmailStr, game_id: int):
    user_joining = get_user_by_email(email=user_email)
    game = get_game_by_id(game_id=game_id)
    for player in game.players:
        if player.user == user_joining:
            return 1
    return 0


@db_session
def save_new_game(owner: EmailStr, name: str,
                  min_players: int, max_players: int):
    owner = get_user_by_email(email=owner)
    game = Game(
        owner=owner,
        name=name,
        creation_date=datetime.today(),
        state=0,
        min_players=min_players,
        max_players=max_players
    )
    board = Board(
        game=game,
        fenix_promulgation=0,
        death_eater_promulgation=0,
        election_counter=0
    )
    commit()
    return game.id


@db_session
def put_new_player_in_game(user: EmailStr, game_id: int):
    if is_player_in_game(user, game_id):
        raise player_already_in_game_exception
    game = get_game_by_id(game_id=game_id)
    if game.players.count() == game.max_players:
        raise max_players_reach_exception
    if game.state == 1 or game.state == 2:
        raise game_has_finished_exception
    creator = get_user_by_email(email=user)
    new_player = Player(
        user=creator,
        is_alive=True,
        game_in=game,
        chat_enabled=True,
        is_investigated=False,
        turn=game.players.count()+1
    )
    commit()
    creator.playing_in.add(Player[new_player.id])
    game.players.add(Player[new_player.id])
    return new_player.id


@db_session
def check_init_conditions(game_id: int, player_id: int):
    game = get_game_by_id(game_id=game_id)
    player_owner = get_player_by_id(player_id=player_id)
    if game.owner == player_owner.user:
        if game.min_players <= game.players.count():
            return 1
    return 0
