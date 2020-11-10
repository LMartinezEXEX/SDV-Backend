from pony.orm import *
from Database.database import *
from Database.game_functions import get_player_by_id, get_player_set, get_game_by_id, set_game_init, assign_roles
import random


'''
Assert if player is alive
'''


@db_session()
def is_alive(game_id: int, player_id: int):
    player = Player.get(lambda p: p.game_in.id ==
                        game_id and p.id == player_id)
    return player.is_alive


'''
Get the number of alive players at the moment in the game
'''


@db_session()
def alive_players_count(game_id: int):
    game = Game[game_id]
    alive_players = Player.select(
        lambda p: p.game_in.id == game_id and p.is_alive)
    return alive_players.count()


'''
Assert if player is the current minister in the current turn
'''


@db_session()
def is_current_minister(game_id: int, player_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return True if turn.current_minister.id == player_id else False


'''
Assert if there was already a promulgation in the current turn
'''


@db_session()
def already_promulgate_in_current_turn(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return turn.promulgated


'''
Get cuantity of turns in the game
'''


@db_session()
def get_current_turn_number_in_game(game_id: int):
    game = Game[game_id]
    return len(game.turn)


'''
Get some turn instance in the game depending the number
'''


@db_session()
def get_turn_in_game(game_id: int, turn_number: int):
    return Turn.get(lambda t: t.game.id ==
                    game_id and t.turn_number == turn_number)


'''
Generate 'quantity' new cards for a game
'''


@db_session()
def generate_card(quantity: int, order_in_deck: int, game_id: int):
    game = Game[game_id]

    random.seed()

    for _ in range(quantity):
        card_type = random.randint(0, 1)
        Card(order=order_in_deck,
             type=card_type,
             game=game,
             discarded=False)
        order_in_deck += 1


'''
Get the next candidate for minister based on players turns and state
'''


@db_session()
def get_next_candidate(players: Set(Player), last_candidate: Player = None):
    next_candidate = None

    if not last_candidate is None:
        next_candidate = players.select(
            lambda p: p.is_alive and p.turn > last_candidate.turn).order_by(
            Player.turn).first()

    if next_candidate is None:
        next_candidate = players.select(
            lambda p: p.is_alive).order_by(
            Player.turn).first()

    return next_candidate


'''
Generate a new turn with its Vote instance
'''


@db_session()
def generate_turn(game_instance: Game, turn_number: int, candidate_minister: Player, candidate_director: Player,
                  current_minister: Player, current_director: Player, last_minister: Player = None, last_director: Player = None):
                              
    turn = Turn(game=game_instance,
                turn_number=turn_number,
                current_minister=current_minister,
                current_director=current_director,
                last_minister=last_minister if last_minister is not None else candidate_minister,
                last_director=last_director if last_director is not None else candidate_director,
                candidate_minister=candidate_minister,
                candidate_director=candidate_director,
                taken_cards=False,
                promulgated=False)
   
    Vote(result=False,
         turn=turn)


'''
Start a new turn and return the candidate for minister in mentioned turn.
If it's the first turn in the game, create three cards to keep always before
giving to the legislative session
'''


@db_session()
def select_MM_candidate(game_id: int):
    game = Game[game_id]
    players_set = game.players
    game_turns = get_current_turn_number_in_game(game_id)

    if game_turns > 0:
        last_turn = get_turn_in_game(game_id=game_id,
                                     turn_number=game_turns)

        last_candidate_minister = last_turn.candidate_minister

        next_candidate_minister = get_next_candidate(
            players_set, last_candidate_minister)

        turn = generate_turn(
            game_instance=game,
            turn_number=game_turns + 1,
            candidate_minister=next_candidate_minister,
            candidate_director=next_candidate_minister,
            last_minister=last_turn.current_minister,
            last_director=last_turn.current_director,
            current_minister=next_candidate_minister,
            current_director=next_candidate_minister)

    # Is the first turn in the game
    else:

        next_candidate_minister = get_next_candidate(players=players_set)

        turn = generate_turn(
            game_instance=game,
            turn_number=game_turns + 1,
            candidate_minister=next_candidate_minister,
            candidate_director=next_candidate_minister,
            last_minister=None,
            last_director=None,
            current_minister=next_candidate_minister,
            current_director=next_candidate_minister)

        # Generate the first set of cards
        generate_card(3, 1, game_id)

    return next_candidate_minister.id


'''
Assert if a player already voted
'''


@db_session()
def player_voted(game_id: int, player_id: int):
    game = Game[game_id]
    player = get_player_by_id(player_id)

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
def vote_turn(game_id: int, player_id: int, player_vote: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    player = get_player_by_id(player_id)
    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn.turn_number and v.turn.game.id == game_id)

    Player_vote(player=player,
                vote=vote,
                is_lumos=True if player_vote else False)

    return len(vote.player_vote)


'''
Get the number of votes currently
'''


@db_session()
def current_votes(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn_number and v.turn.game.id == game_id)

    return len(vote.player_vote)


'''
Get the result from the current Vote and an array of player id's who voted lumos
'''


@db_session()
def get_result(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn_number and v.turn.game.id == game_id)

    lumos = Player_vote.select(
        lambda pv: pv.vote.turn.turn_number == turn.turn_number and pv.is_lumos).count()
    lumos_votes = select(
        pv for pv in Player_vote if pv.vote.turn.turn_number == turn.turn_number and pv.is_lumos)[:]

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
def taked_cards(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    return turn.taken_cards


'''
Return the three cards in order, and create three new cards for future turns
'''


@db_session()
def generate_3_cards(game_id: int):
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

    generate_card(3, game_deck_cuantity + 1, game_id)

    turn.taken_cards = True
    return [cards[0].type, cards[1].type, cards[2].type]


'''
Promulgate a card given by the current minister in the game
If card_type = 0, promulgate for the Fenix Order
If card_type = 1, promulgate for the Death Eaters
'''


@db_session()
def promulgate(game_id: int, card_type: int):
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
def check_status(game_id: int):
    game = Game[game_id]
    turn_number = get_current_turn_number_in_game(game_id)
    game_finished = False

    if turn_number == 0:
        return [game_finished, 0, 0, None, None]

    turn = get_turn_in_game(game_id, turn_number)
    board = Board[game_id]

    if board.fenix_promulgation == 5 or board.death_eater_promulgation == 6 or (
            board.death_eater_promulgation >= 3 and turn.current_director.rol == "Voldemort"):
        game_finished = True
        game.state = 2

    return [game_finished, board.fenix_promulgation, board.death_eater_promulgation,
            turn.current_minister.id, turn.current_director.id]



# -------------------------------------------------------

@db_session()
def create_first_turn(game_id: int):
    game = get_game_by_id(game_id=game_id)
    players_set = get_player_set(game_id=game_id)
    next_minister = get_next_candidate(players_set)
    generate_turn(
        game_instance=game,
        turn_number=1,
        candidate_minister=next_minister,
        candidate_director=next_minister,
        last_minister=None,
        last_director=None,
        current_minister=next_minister,
        current_director=next_minister)
    generate_card(3,1,game_id)
    assign_roles(game_id=game_id)
    set_game_init(game_id)
    return next_minister.id


@db_session()
def get_not_discarded_cards(game_id: int):
    game = get_game_by_id(game_id=game_id)
    game_deck_quantity = game.card.count()

    cards = Card.select(
        lambda c: c.game.id == game_id and c.order > (
            game_deck_cuantity -
            3) and c.discarded == False)

    return [cards[0].type, cards[1].type]


@db_session()
async def discard_card(game_id: int, data: int):
    game = get_game_by_id(game_id=game_id)
    deck_quantity = game.cards.count()
    
    card = Card.select(
        lambda c: c.game.id == game_id and
        c.order > (deck_quantity - 3) and
        c.type == data 
        )[:1]
    
    card.discarded = True
    return get_not_discarded_cards(game_id=game_id)


    

# -------------------------------------------------------