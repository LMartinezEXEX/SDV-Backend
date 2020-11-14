from datetime import datetime
from pony.orm import *
from Database.database import Player, User, Game, Board, db
from pydantic import EmailStr
from fastapi import HTTPException, status
from API.Model.gameExceptions import *
from numpy import random
from Database.roles_constants import *


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
def players_in_game(game_id: int):
    game = Game[game_id]
    return game.players.count()


@db_session()
def get_game_state(game_id):
    try:
        game = Game[game_id]
        state = game.state
    except BaseException:
        state = -1

    return state

@db_session()
def get_player_rol_and_loyalty(player_id: int):
    player = get_player_by_id(player_id=player_id)
    return {"Rol": player.rol, "Loyalty": player.loyalty}


@db_session()
def set_game_init(game_id: int):
    Game[game_id].state = 1


@db_session
def is_player_in_game_by_email(user_email: EmailStr, game_id: int):
    user_joining = get_user_by_email(email=user_email)
    game = get_game_by_id(game_id=game_id)
    for player in game.players:
        if player.user == user_joining:
            return 1
    return 0


@db_session
def get_player_set(game_id: int):
    game = get_game_by_id(game_id= game_id)
    return game.players

@db_session()
def is_player_in_game_by_id(game_id: int, player_id: int):
    return True if Player.get(
        lambda p: p.game_in.id == game_id and p.id == player_id) is not None else False


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
        election_counter=0,
        spell_available=False
    )
    commit()
    return game.id


@db_session
def put_new_player_in_game(user: EmailStr, game_id: int):
    game = get_game_by_id(game_id=game_id)
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
def check_create_conditions(user_email: EmailStr, name: str,
                            min_players: int, max_players: int):
    user = get_user_by_email(user_email)
    if not user:
        raise user_not_found_exception
    if min_players < 5:
        raise less_than_five_players_exception
    if max_players < min_players:
        raise incoherent_amount_of_players_exception
    if max_players > 10:
        raise more_than_ten_players_exception


@db_session 
def check_join_conditions(game_id: int, user_email: EmailStr):
    game = get_game_by_id(game_id=game_id)
    if not game:
        raise game_not_found_exception
    user = get_user_by_email(email=user_email)
    if not user:
        raise user_not_found_exception
    if is_player_in_game_by_email(user_email, game_id):
        raise player_already_in_game_exception
    if game.players.count() >= game.max_players:
        raise max_players_reach_exception
    if game.state == 1:
        raise game_has_started_exception
    if game.state == 2:
        raise game_has_finished_exception


@db_session
def check_init_conditions(game_id: int, player_id: int):
    game = get_game_by_id(game_id=game_id)
    if not game:
        raise game_not_found_exception
    player = get_player_by_id(player_id=player_id)
    if not player:
        raise player_not_found_exception
    if player not in game.players:
        raise player_not_in_game_exception
    if game.state == 1:
        raise game_has_started_exception
    if game.state == 2:
        raise game_has_finished_exception
    if game.owner != player.user:
        raise not_the_owner_exception
    if game.min_players > game.players.count():
        raise min_player_not_reach_exception


@db_session
def assign_roles(game_id: int):
    game = get_game_by_id(game_id=game_id)
    amount_players = game.players.count()
    roles = select_roles_for_game(players=amount_players)
    mixed_roles = random.choice(roles, amount_players, replace=False)
    index = 0
    for player in game.players:
        player.rol = mixed_roles[index]
        player.loyalty = get_loyalty(rol=mixed_roles[index])
        index = index+1
    

@db_session()
def get_game_list():
    games = Game.select(lambda g: g.state == 0)
    g_list = []
    for game in games:
        g_list.append(
            {
             "id": game.id,
             "name": game.name,
             "owner": game.owner.username,
             "min_players": game.min_players,
             "max_players": game.max_players,
             "players": game.players.count()
            }
        )
    return g_list


@db_session()
def get_current_users_in_game(game_id: int):
    game = get_game_by_id(game_id=game_id)
    user_list = []
    for user in game.players.user:
        user_list.append(
            {"username": user.username}
        )
    return user_list