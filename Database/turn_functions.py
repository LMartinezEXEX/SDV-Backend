from pony.orm import *
from Database.database import *
import random


@db_session()
def get_player_in_game(game_id, player_id):
    game = Game[game_id]
    return game.player.select(lambda p: p.id==player_id).first()


@db_session()
def is_player_in_game(game_id, player_id):
    return True if Player.get(lambda p: p.game_in.id==game_id and p.id==player_id) is not None else False


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
    game_turns = len(game.turn)

    if game_turns > 0:
        print(len(game.turn))
        last_turn = get_turn_in_game(game_id=game_id,
                                     turn_number=game_turns)

        print(last_turn)
        last_candidate_minister = last_turn.candidate_minister

        next_candidate_minister = players_set.select(lambda p: p.is_alive and p.turn > last_candidate_minister.turn).order_by(Player.turn).first()

        # Start the round again
        if next_candidate_minister is None:
            next_candidate_minister = players_set.select(lambda p: p.is_alive).order_by(Player.turn).first()

        Turn(game=game,
             turn_number=game_turns+1,
             current_minister=next_candidate_minister,
             current_director=next_candidate_minister,
             last_minister=last_turn.current_minister,
             last_director=last_turn.current_director,
             candidate_minister=next_candidate_minister,
             candidate_director=next_candidate_minister,
             taken_cards=False)

    # Is the first turn in the game
    else:
        next_candidate_minister = players_set.select(lambda p: p.is_alive).order_by(Player.turn).first()

        turn = Turn(game=game,
                     turn_number=game_turns+1,
                     current_minister=next_candidate_minister,
                     current_director=next_candidate_minister,
                     last_minister=next_candidate_minister,
                     last_director=next_candidate_minister,
                     candidate_minister=next_candidate_minister,
                     candidate_director=next_candidate_minister,
                     taken_cards=False)

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


@db_session()
def player_voted(game_id, player_id):
    game = Game[game_id]
    player = game.player.select(lambda p: p.id == player_id).first()

    turn_number = len(game.turn)
    turn = get_turn_in_game(game_id, turn_number)

    vote = Vote.get(lambda v: v.turn.turn_number==turn.turn_number and v.turn.game.id==game_id)

    voted = False
    # No one voted yet in this turn
    if vote is None:
        return voted

    if Player_vote.get(lambda pv: pv.player.id==player_id and pv.vote.turn==turn) is not None:
        voted = True

    return voted


@db_session()
def vote_turn(game_id, player_id, player_vote):
    game = Game[game_id]
    turn_number = len(game.turn)
    turn = get_turn_in_game(game_id, turn_number)
    player = get_player_in_game(game_id, player_id)
    vote = Vote.get(lambda v: v.turn.turn_number == turn.turn_number and v.turn.game.id==game_id)

    # Is the first vote in the current turn
    if vote is None:
        vote = Vote(result=False,
                    turn=turn)

        Player_vote(player=player,
                    vote = vote,
                    is_lumos= True if player_vote else False)

    else:
        Player_vote(player=player,
                    vote = vote,
                    is_lumos= True if player_vote else False)

    return len(vote.player_vote)


@db_session()
def current_votes(game_id):
    game = Game[game_id]

    turn_number = len(game.turn)
    turn = get_turn_in_game(game_id, turn_number)

    vote = Vote.get(lambda v: v.turn.turn_number == turn_number)

    # No one voted yet
    if vote is None:
        return 0

    return len(vote.player_vote)


@db_session()
def alive_players(game_id):
    game = Game[game_id]
    alive_players = Player.select(lambda p: p.game_in.id==game_id and p.is_alive)
    return alive_players.count()


@db_session()
def get_result(game_id):
    game = Game[game_id]
    turn_number = len(game.turn)
    turn = get_turn_in_game(game_id, turn_number)
    vote = Vote.get(lambda v: v.turn.turn_number == turn_number)

    lumos = Player_vote.select(lambda pv: pv.vote.id==vote.id and pv.is_lumos).count()
    lumos_votes = select(pv for pv in Player_vote if pv.vote.id==vote.id and pv.is_lumos)[:]

    player_ids = []
    for _vote_ in lumos_votes:
        player_ids.append(_vote_.player.id)

    result = False
    if len(vote.player_vote) - lumos < lumos:
        result = True

    vote.result = result
    return [result, player_ids]


@db_session()
def taked_cards(game_id):
    game = Game[game_id]
    turn = get_turn_in_game(game_id, len(game.turn))

    return turn.taken_cards


'''
Generate 3 new cards and return the previous 3 cards type
'''
@db_session()
def generate_3_cards(game_id):
    game = Game[game_id]
    turn = get_turn_in_game(game_id, len(game.turn))
    game_deck_cuantity = len(game.card)

    cards = Card.select(lambda c: c.game.id==game_id and c.order > (game_deck_cuantity - 3)).order_by(Card.order)[:3]

    for _ in range(3):
        game_deck_cuantity += 1
        card_type = random.randint(0,1)
        Card(order=game_deck_cuantity,
             type=card_type,
             turn=turn,
             game=game)

    turn.taken_cards = True
    return [cards[0].type, cards[1].type, cards[2].type]
