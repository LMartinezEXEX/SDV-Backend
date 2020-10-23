from pony.orm import *
from Database.database import *
import random


@db_session()
def get_player_in_game(game_id, player_id):
    game = Game[game_id]
    return game.player.select(lambda p: p.id==player_id).first()


@db_session()
def is_alive(game_id, player_id):
    player = Player.get(lambda p: p.game_in.id==game_id and p.id==player_id)
    return player.is_alive


@db_session()
def get_current_turn_number_in_game(game_id):
    game = Game[game_id]
    return len(game.turn)


@db_session()
def get_turn_in_game(game_id, turn_number):
    return Turn.get(lambda t: t.game.id==game_id and t.turn_number==turn_number)


@db_session()
def select_MM_candidate(game_id):
    game = Game[game_id]
    players_set = game.player
    next_candidate_minister = None

    if len(game.turn) > 0:
        last_turn = get_turn_in_game(game_id=game_id,
                                     turn_number=len(game.turn))

        last_candidate_minister = last_turn.candidate_minister

        next_candidate_minister = players_set.select(lambda p: p.is_alive and p.turn > last_candidate_minister.turn).order_by(Player.turn).first()

        # Start the round again
        if next_candidate_minister is None:
            next_candidate_minister = players_set.select(lambda p: p.is_alive).order_by(Player.turn).first()

        Turn(game=game,
             current_minister=next_candidate_minister,
             current_director=next_candidate_minister,
             last_minister=last_turn.current_minister,
             last_director=last_turn.current_director,
             candidate_minister=next_candidate_minister,
             candidate_director=next_candidate_minister)

    # Is the first turn in the game
    else:
        next_candidate_minister = players_set.select(lambda p: p.is_alive).order_by(Player.turn).first()

        turn = Turn(game=game,
                     current_minister=next_candidate_minister,
                     current_director=next_candidate_minister,
                     last_minister=next_candidate_minister,
                     last_director=next_candidate_minister,
                     candidate_minister=next_candidate_minister,
                     candidate_director=next_candidate_minister)

        #Generate the first set of cards
        order = 1
        for _ in range(3):
            card_type = random.randint(0,1)
            Card(order=order,
                 type=card_type,
                 turn=turn,
                 game=game)
            order += 1

    return next_candidate_minister.id
