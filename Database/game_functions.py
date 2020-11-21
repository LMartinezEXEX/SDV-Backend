from pony import orm
from datetime import datetime
from pydantic import EmailStr
from numpy import random
from Database.database import *
import Database.aux_functions as aux
import Database.user_functions as db_user
import Database.player_functions as db_player
import Database.turn_functions as db_turn
from API.Model.exceptions import *

@orm.db_session
def get_game_by_id(game_id: int):
    return Game.get(id=game_id)


@orm.db_session
def players_in_game(game_id: int):
    game = Game[game_id]
    return game.players.count()


@orm.db_session
def get_game_state(game_id):
    try:
        game = Game[game_id]
        state = game.state
    except BaseException:
        state = -1

    return state


@orm.db_session
def set_game_init(game_id: int):
    Game[game_id].state = 1


@orm.db_session
def get_player_set(game_id: int):
    game = get_game_by_id(game_id= game_id)
    return game.players


@orm.db_session
def save_new_game(owner: EmailStr, name: str,
                  min_players: int, max_players: int):
    owner = db_user.get_user_by_email(email=owner)
    game = Game(
        owner=owner,
        name=name,
        creation_date=datetime.datetime.today(),
        state=0,
        min_players=min_players,
        max_players=max_players,
        end_game_notified=[]
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


@orm.db_session
def check_create_conditions(user_email: EmailStr, name: str,
                            min_players: int, max_players: int):
    user = db_user.get_user_by_email(user_email)
    if not user:
        raise user_not_found_exception
    if min_players < 5:
        raise less_than_five_players_exception
    if max_players < min_players:
        raise incoherent_amount_of_players_exception
    if max_players > 10:
        raise more_than_ten_players_exception


@orm.db_session
def check_join_conditions(game_id: int, user_email: EmailStr):
    game = get_game_by_id(game_id=game_id)
    if not game:
        raise game_not_found_exception
    user = db_user.get_user_by_email(email=user_email)
    if not user:
        raise user_not_found_exception
    if db_player.is_player_in_game_by_email(user_email, game_id):
        raise player_already_in_game_exception
    if game.players.count() >= game.max_players:
        raise max_players_reach_exception
    if game.state == 1:
        raise game_has_started_exception
    if game.state == 2:
        raise game_has_finished_exception


@orm.db_session
def check_init_conditions(game_id: int, player_id: int):
    game = get_game_by_id(game_id=game_id)
    if not game:
        raise game_not_found_exception
    player = db_player.get_player_by_id(player_id=player_id)
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


@orm.db_session
def remove_player_from_game(game_id: int, user_email: EmailStr):
    game = get_game_by_id(game_id=game_id)
    for player in game.players:
        if player.user.email == user_email:
            game.players.remove(player)
            return "Player removed OK"
    raise player_not_found_exception


@orm.db_session
def delete_game(game_id: int):
    Game[game_id].delete()
    if not get_game_by_id(game_id):
        return "The game was successfully deleted"
    else:
        raise game_not_deleted_exception

@orm.db_session
def assign_roles(game_id: int):
    game = get_game_by_id(game_id=game_id)
    amount_players = game.players.count()
    roles = aux.select_roles_for_game(players=amount_players)
    mixed_roles = random.choice(roles, amount_players, replace=False)
    index = 0
    for player in game.players:
        player.rol = mixed_roles[index]
        player.loyalty = aux.get_loyalty(rol=mixed_roles[index])
        index = index+1


@orm.db_session
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


@orm.db_session
def get_current_users_in_game(game_id: int):
    game = get_game_by_id(game_id=game_id)
    user_list = []
    for user in game.players.user:
        user_list.append(
            {"username": user.username}
        )
    return user_list


'''
Get the number of alive players at the moment in the game
'''


@orm.db_session
def alive_players_count(game_id: int):
    game = Game[game_id]
    alive_players = Player.select(
    lambda p: p.game_in.id == game_id and p.is_alive)
    return alive_players.count()


'''
Get all players id in the game
'''


@orm.db_session
def get_all_players_id(game_id: int):
    game = Game[game_id]
    players = game.players.order_by(Player.id)

    return aux.create_players_id_list(players)


'''
Get players ids, username and loyalty in current game
'''

@orm.db_session
def get_players_info(game_id):
    players_id_list = get_all_players_id(game_id)

    players_info_list = []
    for id in players_id_list:
        player = db_player.get_player_by_id(id)
        players_info_list.append({"player_id": id,
                                  "username": player.user.username,
                                  "loyalty": player.loyalty})

    return players_info_list


'''
Get the state of the 'in Game' game, to know if a team won or not
'''


@orm.db_session
def check_status(game_id: int):
    game = Game[game_id]
    turn_number = db_turn.get_current_turn_number_in_game(game_id)
    game_finished = False

    if turn_number == 0:
        return [game_finished, 0, 0, None, None]

    turn = db_turn.get_turn_in_game(game_id, turn_number)
    board = Board[game_id]

    if board.fenix_promulgation == 5 or board.death_eater_promulgation == 6 \
        or (board.death_eater_promulgation >= 3 \
            and turn.current_director != turn.current_minister \
            and turn.current_director.rol == "Voldemort") \
        or not (next(player for player in game.players if player.rol == "Voldemort").is_alive):
        game_finished = True

    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn.turn_number and v.turn.game.id == game_id)

    return [game_finished, board.fenix_promulgation, board.death_eater_promulgation,
            turn.current_minister.id, turn.current_director.id, len(vote.player_vote) == alive_players_count(game_id)]
