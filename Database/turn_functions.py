from pony.orm import *
from Database.database import *
import random


# -GAME-FUNCTION-----------------------------------------------------------------
@db_session()
def get_game_state(game_id):
    try:
        game = Game[game_id]
        state = game.state
    except BaseException:
        state = -1

    return state
# -------------------------------------------------------------------------------


'''
Get player instance in game. Should previously assert player is in the game
'''


@db_session()
def get_player_in_game(game_id, player_id):
    game = Game[game_id]
    return game.player.select(lambda p: p.id == player_id).first()


'''
Assert if a player is in the game
'''


@db_session()
def is_player_in_game(game_id, player_id):
    return True if Player.get(
        lambda p: p.game_in.id == game_id and p.id == player_id) is not None else False


'''
Assert if player is alive
'''


@db_session()
def is_alive(game_id, player_id):
    player = Player.get(lambda p: p.game_in.id ==
                        game_id and p.id == player_id)
    return player.is_alive


'''
Get the number of alive players at the moment in the game
'''


@db_session()
def alive_players_count(game_id):
    game = Game[game_id]
    alive_players = Player.select(
        lambda p: p.game_in.id == game_id and p.is_alive)
    return alive_players.count()


'''
Assert if player is the current minister in the current turn
'''


@db_session()
def is_current_minister(game_id, player_id):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return True if turn.current_minister.id == player_id else False


'''
Assert if there was already a promulgation in the current turn
'''


@db_session()
def already_promulgate_in_current_turn(game_id):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return turn.promulgated


'''
Get cuantity of turns in the game
'''


@db_session()
def get_current_turn_number_in_game(game_id):
    game = Game[game_id]
    return len(game.turn)


'''
Get some turn instance in the game depending the number
'''


@db_session()
def get_turn_in_game(game_id, turn_number):
    return Turn.get(lambda t: t.game.id ==
                    game_id and t.turn_number == turn_number)


'''
Start a new turn and return the candidate for minister in mentioned turn.
If it's the first turn in the game, create three cards to keep always before
giving to the legislative session
'''


@db_session()
def select_MM_candidate(game_id):
    game = Game[game_id]
    players_set = game.player
    next_candidate_minister = None
    game_turns = get_current_turn_number_in_game(game_id)

    if game_turns > 0:

        last_turn = get_turn_in_game(game_id=game_id,
                                     turn_number=game_turns)

        print(last_turn)
        last_candidate_minister = last_turn.candidate_minister

        next_candidate_minister = players_set.select(
            lambda p: p.is_alive and p.turn > last_candidate_minister.turn).order_by(
            Player.turn).first()

        # Start the round again
        if next_candidate_minister is None:
            next_candidate_minister = players_set.select(
                lambda p: p.is_alive).order_by(
                Player.turn).first()

        Turn(game=game,
             turn_number=game_turns + 1,
             current_minister=next_candidate_minister,
             current_director=next_candidate_minister,
             last_minister=last_turn.current_minister,
             last_director=last_turn.current_director,
             candidate_minister=next_candidate_minister,
             candidate_director=next_candidate_minister,
             taken_cards=False,
             promulgated=False)

    # Is the first turn in the game
    else:

        # This should be done in game creation
        board = Board(game=game,
                      fenix_promulgation=0,
                      death_eater_promulgation=0,
                      election_counter=0)

        next_candidate_minister = players_set.select(
            lambda p: p.is_alive).order_by(
            Player.turn).first()

        turn = Turn(game=game,
                    turn_number=game_turns + 1,
                    current_minister=next_candidate_minister,
                    current_director=next_candidate_minister,
                    last_minister=next_candidate_minister,
                    last_director=next_candidate_minister,
                    candidate_minister=next_candidate_minister,
                    candidate_director=next_candidate_minister,
                    taken_cards=False,
                    promulgated=False)

        # Generate the first set of cards
        order = 1
        for _ in range(3):
            card_type = random.randint(0, 1)
            Card(order=order,
                 type=card_type,
                 turn=turn,
                 game=game)
            order += 1

    return next_candidate_minister.id


'''
Assert if a player already voted
'''


@db_session()
def player_voted(game_id, player_id):
    game = Game[game_id]
    player = get_player_in_game(game_id, player_id)

    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn.turn_number and v.turn.game.id == game_id)

    voted = False
    # No one voted yet in this turn
    if vote is None:
        return voted

    if Player_vote.get(lambda pv: pv.player.id ==
                       player_id and pv.vote.turn == turn) is not None:
        voted = True

    return voted


'''
Submit a player's vote instance.
If it is the first vote in the turn, create the Vote instance for the turn.
'''


@db_session()
def vote_turn(game_id, player_id, player_vote):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    player = get_player_in_game(game_id, player_id)
    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn.turn_number and v.turn.game.id == game_id)

    # Is the first vote in the current turn
    if vote is None:
        vote = Vote(result=False,
                    turn=turn)

        Player_vote(player=player,
                    vote=vote,
                    is_lumos=True if player_vote else False)

    else:
        Player_vote(player=player,
                    vote=vote,
                    is_lumos=True if player_vote else False)

    return len(vote.player_vote)


'''
Get the number of votes currently
'''


@db_session()
def current_votes(game_id):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    vote = Vote.get(lambda v: v.turn.turn_number == turn_number)

    # No one voted yet
    if vote is None:
        return 0

    return len(vote.player_vote)


'''
Get the result from the current Vote and an array of player id's who voted lumos
'''


@db_session()
def get_result(game_id):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    vote = Vote.get(lambda v: v.turn.turn_number == turn_number)

    lumos = Player_vote.select(
        lambda pv: pv.vote.id == vote.id and pv.is_lumos).count()
    lumos_votes = select(
        pv for pv in Player_vote if pv.vote.id == vote.id and pv.is_lumos)[:]

    player_ids = []
    for _vote_ in lumos_votes:
        player_ids.append(_vote_.player.id)

    result = False
    if len(vote.player_vote) - lumos < lumos:
        result = True

    vote.result = result
    return [result, player_ids]


'''
Assert if the three cards for legislative session have been taken
'''


@db_session()
def taked_cards(game_id):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    return turn.taken_cards


'''
Return the three cards in order, and create three new cards for future turns
'''


@db_session()
def generate_3_cards(game_id):
    game = Game[game_id]
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    game_deck_cuantity = len(game.card)

    cards = Card.select(
        lambda c: c.game.id == game_id and c.order > (
            game_deck_cuantity -
            3)).order_by(
        Card.order)[
                :3]

    for _ in range(3):
        game_deck_cuantity += 1
        card_type = random.randint(0, 1)
        Card(order=game_deck_cuantity,
             type=card_type,
             turn=turn,
             game=game)

    turn.taken_cards = True
    return [cards[0].type, cards[1].type, cards[2].type]


'''
Promulgate a card given by the current minister in the game
If card_type = 0, promulgate for the Fenix Order
If card_type = 1, promulgate for the Death Eaters
'''


@db_session()
def promulgate(game_id, card_type):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    board = Board[game_id]

    if card_type:
        board.death_eater_promulgation += 1
    else:
        board.fenix_promulgation += 1

    turn.promulgated = True
    return [board.fenix_promulgation, board.death_eater_promulgation]


'''
Get the state of the 'in Game' game, to know if a team won or not
'''


@db_session()
def check_status(game_id):
    game = Game[game_id]
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    board = Board[game_id]

    game_finished = False

    if board.fenix_promulgation == 5 or board.death_eater_promulgation == 6 or (
        board.death_eater_promulgation >= 3 and turn.current_director.rol == "Voldemort"):
        game_finished = True
        game.state = 2

    return [game_finished, board.fenix_promulgation, board.death_eater_promulgation,
            turn.current_minister.id, turn.current_director.id]
