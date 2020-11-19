from pony import orm
from Database.database import *
import Database.turn_functions as db_turn
import Database.player_functions as db_player
import Database.game_functions as db_game

'''
Submit a player's vote instance.
If it is the first vote in the turn, create the Vote instance for the turn.
'''


@orm.db_session
def vote_turn(game_id: int, player_id: int, player_vote: bool):
    turn_number = db_turn.get_current_turn_number_in_game(game_id)
    turn = db_turn.get_turn_in_game(game_id, turn_number)
    player = db_player.get_player_by_id(player_id)
    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn.turn_number and v.turn.game.id == game_id)

    Player_vote(player=player,
                vote=vote,
                is_lumos= player_vote)
    commit()

    # Check and take action if all players voted
    if len(vote.player_vote) == db_game.alive_players_count(game_id):
        lumos_counter = select(
            pv for pv in Player_vote if pv.vote.turn.turn_number == turn.turn_number and pv.vote.turn.game.id == game_id and pv.is_lumos).count()

        result = False
        if len(vote.player_vote) - lumos_counter < lumos_counter:
            # candidates were elected, restart board counter
            board = Board[game_id]
            board.election_counter = 0

            result = True
            turn.current_minister = turn.candidate_minister
            turn.current_director = turn.candidate_director

        vote.result = result


    return len(vote.player_vote)


'''
Get the number of votes currently
'''


@orm.db_session
def current_votes(game_id: int):
    turn_number = db_turn.get_current_turn_number_in_game(game_id)
    turn = db_turn.get_turn_in_game(game_id, turn_number)

    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn_number and v.turn.game.id == game_id)

    return len(vote.player_vote)


'''
Get the result from the current Vote and an array of player id's who voted lumos
'''


@orm.db_session
def get_result(game_id: int):
    turn_number = db_turn.get_current_turn_number_in_game(game_id)
    turn = db_turn.get_turn_in_game(game_id, turn_number)
    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn_number and v.turn.game.id == game_id)

    lumos_votes = select(pv for pv in Player_vote if pv.vote.turn.turn_number == turn.turn_number and pv.vote.turn.game.id == game_id and pv.is_lumos)[:]

    player_ids = []
    for _vote_ in lumos_votes:
        player_ids.append(_vote_.player.id)

    return [vote.result, player_ids]
