from pony import orm
from pydantic import EmailStr
from Database.database import *
import Database.turn_functions as db_turn
import Database.user_functions as db_user
import Database.game_functions as db_game
from API.Model.exceptions import player_is_dead_exception

@orm.db_session
def get_player_by_id(player_id: int):
    return Player.get(id=player_id)

@orm.db_session
def get_player_rol_and_loyalty(player_id: int):
    player = get_player_by_id(player_id=player_id)
    return {"Rol": player.rol, "Loyalty": player.loyalty}

@orm.db_session
def is_player_in_game_by_email(user_email: EmailStr, game_id: int):
    user_joining = db_user.get_user_by_email(email=user_email)
    game = db_game.get_game_by_id(game_id=game_id)
    for player in game.players:
        if player.user == user_joining:
            return 1
    return 0

@orm.db_session
def is_player_in_game_by_id(game_id: int, player_id: int):
    return Player.get(lambda p: p.game_in.id == game_id and p.id == player_id)

@orm.db_session
def put_new_player_in_game(user: EmailStr, game_id: int):
    game = db_game.get_game_by_id(game_id=game_id)
    creator = db_user.get_user_by_email(email=user)
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


'''
Assert if player is alive
'''


@orm.db_session
def is_alive(game_id: int, player_id: int):
    player = Player.get(lambda p: p.game_in.id ==
                        game_id and p.id == player_id)
    return player.is_alive


'''
Assert if a player was investigated previously
'''


@orm.db_session
def is_player_investigated(player_id: int):
    player = get_player_by_id(player_id)
    return player.is_investigated


'''
Assert if a player already voted
'''


@orm.db_session
def player_voted(game_id: int, player_id: int):
    game = Game[game_id]
    player = get_player_by_id(player_id)

    turn_number = db_turn.get_current_turn_number_in_game(game_id)
    turn = db_turn.get_turn_in_game(game_id, turn_number)

    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn.turn_number and v.turn.game.id == game_id)

    voted = False
    # No one voted yet in this turn
    if vote is None:
        return voted

    if Player_vote.get(lambda pv: pv.player.id == player_id and
                    pv.vote.turn == turn and pv.vote.turn.game.id == game_id):
        voted = True

    return voted


@orm.db_session
def notify_with_player(game_id: int, player_id: int):
    turn_number = db_turn.get_current_turn_number_in_game(game_id)
    turn = db_turn.get_turn_in_game(game_id, turn_number)
    player = get_player_by_id(player_id)
    if player.is_alive:
        # If player has notified, don't let him do this again
        if player_id in turn.reject_notified:
            return { "notified": True }

        alive_players = db_game.alive_players_count(game_id)
        if len(turn.reject_notified) < alive_players:
            turn.reject_notified.append(player_id)

            # All players know that candidates were rejected, then go to next turn
            if len(turn.reject_notified) == alive_players:
                db_turn.select_MM_candidate(game_id)

        return { "notified": True }
    else:
        raise player_is_dead_exception
