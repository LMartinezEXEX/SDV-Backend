from pony.orm import *
from Database.database import *
from Database.game_functions import get_player_by_id, get_game_by_id, get_player_set, assign_roles, set_game_init
import random
from API.Model.turnExceptions import invalid_card_type_exception


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
Assert if the director candidate was already selected in the current turn
'''


@db_session()
def already_selected_director_candidate(game_id):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return True if turn.candidate_minister.id != turn.candidate_director.id else False


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
Assert if a player was investigated previously
'''


@db_session()
def is_player_investigated(player_id: int):
    player = get_player_by_id(player_id)
    return player.is_investigated


'''
Assert if there is a savilable spell to execute
'''

@db_session()
def is_board_available_spell(game_id):
    return Board[game_id].spell_available


'''
Get all players id in the game
'''


@db_session()
def get_all_players_id(game_id: int):
    game = Game[game_id]
    players = game.players.order_by(Player.id)

    return create_players_id_list(players)


'''
Create a list of player ids based on the input 'players' array of Player
'''


def create_players_id_list(players):
    player_ids = []

    for player in players:
        player_ids.append(player.id)

    return player_ids


'''
Get players ids, username and loyalty in current game
'''

@db_session()
def get_players_info(game_id):
    players_id_list = get_all_players_id(game_id)

    players_info_list = []
    for id in players_id_list:
        player = get_player_by_id(id)
        players_info_list.append({"player_id": id,
                                  "username": player.user.username,
                                  "loyalty": player.loyalty})

    return players_info_list


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
def generate_turn(game_instance: Game, turn_number: int, candidate_minister: Player,
                  candidate_director: Player, current_minister: Player, current_director: Player,
                  last_minister: Player = None, last_director: Player = None):
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
Create a list of suitable player ids for director candidate
'''


@db_session()
def create_director_candidates_list(game_id, players, previous_formula_vote):
    if previous_formula_vote is None:
        return create_players_id_list(players)

    alive_players_counter = alive_players_count(game_id)
    previous_accepted_formula_turn = previous_formula_vote.turn

    previous_director_id = previous_accepted_formula_turn.candidate_director.id
    previous_minister_id = previous_accepted_formula_turn.candidate_minister.id

    player_ids = []
    for player in players:
        if alive_players_counter == 5 and player.id != previous_director_id:
            player_ids.append(player.id)

        elif player.id != previous_minister_id and player.id != previous_director_id:
            player_ids.append(player.id)

    return player_ids


'''
Get a list of player ids suitable for director candidate
'''


@db_session()
def director_available_candidates(game_id):
    current_turn_number = get_current_turn_number_in_game(game_id)
    current_turn = get_turn_in_game(game_id, current_turn_number)

    regular_alive_players = Player.select(
        lambda p: p.is_alive and p.game_in.id == game_id and p.id != current_turn.candidate_minister.id)[:]

    previous_accepted_formula = Vote.select(
        lambda v: v.result and v.turn.turn_number < current_turn_number and v.turn.game.id == game_id).order_by(
        desc(
            Vote.turn)).first()

    return create_director_candidates_list(
        game_id, regular_alive_players, previous_accepted_formula)


'''
Set a player as director candidate in current turn.
This function doesn't make checks, it should've been made privously
'''


@db_session()
def select_DD_candidate(game_id, player_id):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    director_candidate_player = get_player_by_id(player_id)

    turn.candidate_director = director_candidate_player

    return [turn.candidate_minister.id, director_candidate_player.id]


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
                       player_id and pv.vote.turn == turn and pv.vote.turn.game.id == game_id) is not None:
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
        lambda pv: pv.vote.turn.turn_number == turn.turn_number and pv.vote.turn.game.id == game_id and pv.is_lumos).count()
    lumos_votes = select(
        pv for pv in Player_vote if pv.vote.turn.turn_number == turn.turn_number and pv.vote.turn.game.id == game_id and pv.is_lumos)[:]

    player_ids = []
    for _vote_ in lumos_votes:
        player_ids.append(_vote_.player.id)

    result = False
    if len(vote.player_vote) - lumos < lumos:
        result = True
        turn.current_minister = turn.candidate_minister
        turn.current_director = turn.candidate_director

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
        lambda c: c.game.id == game_id and c.order > (game_deck_cuantity - 3)
        ).order_by(Card.order)[:3]

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
        check_available_spell(game_id)
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


'''
Generate first turn when game starts and therefore isnt a last minister or director
'''


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


'''
Get minister id in current turn
'''


@db_session()
def get_current_minister(game_id: int):
    game = get_game_by_id(game_id=game_id)
    turn_number = get_current_turn_number_in_game(game_id=game_id)
    turn = get_turn_in_game(game_id=game_id, turn_number=turn_number)
    return turn.current_minister.id

'''
Assert if a player is the current director
'''


@db_session()
def is_current_director(game_id: int, player_id: int):
    turn_number = get_current_turn_number_in_game(game_id=game_id)
    turn = get_turn_in_game(game_id=game_id, turn_number=turn_number)
    return turn.current_director.id == player_id

'''
Get cards not discarded from the deck for the director
'''


@db_session()
def get_not_discarded_cards(game_id: int):
    game = get_game_by_id(game_id=game_id)
    game_deck_quantity = len(game.card)
    card_list = []
    cards = Card.select(
        lambda c: (c.game.id == game_id) and
        (c.order > (game_deck_quantity - 6)) and
        (c.order <= (game_deck_quantity - 3)) and
         (not c.discarded)
        ).order_by(Card.order)[:2]
    for card in cards:
        card_list.append(card.type)
    return card_list

'''
Mark a card as discarded in the deck
'''


@db_session()
def discard_card(game_id: int, data: int):
    game = get_game_by_id(game_id=game_id)
    deck_quantity = len(game.card)
    card = Card.select(
        lambda c: (c.game.id == game_id) and (c.order > (deck_quantity - 6)) and (c.type == data)
        ).order_by(Card.order).first()
    if not card:
        raise invalid_card_type_exception
    card.discarded = True
    if not card.discarded:
        raise not_discarded_exception
    return {"message": "Card discarded"}

'''
Check if with current promulgations a spell is available
'''


@db_session()
def check_available_spell(game_id: int):
    board = Board[game_id]
    death_eater_promulgation = board.death_eater_promulgation
    player_cuantity = Game[game_id].players.count()

    #The 'and death_eater_promulgation < 4' should be removed in next spint
    if (player_cuantity == 5 or player_cuantity ==
            6) and death_eater_promulgation >= 3 and death_eater_promulgation < 4:
        board.spell_available = True

    elif (player_cuantity == 7 or player_cuantity == 8) and death_eater_promulgation >= 2 and death_eater_promulgation < 4:
        board.spell_available = True

    elif (player_cuantity == 9 or player_cuantity == 10) and death_eater_promulgation >= 1 and death_eater_promulgation < 4:
        board.spell_available = True

'''
Get current turn in game
'''


@db_session()
def get_current_turn_in_game(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id)

    return get_turn_in_game(game_id, turn_number)

'''
Get available spell string in a game with 5 or 6 players
'''


def available_spell_in_board_1(player_cuantity: int, promulgations: int):
    if promulgations == 3:
        spell = "Guessing"
    #elif promulgations == 4 or promulgations == 5:
    #    spell = "Avada Kedavra"
    else:
        spell = ""

    return spell


'''
Get available spell string in a game with 7 or 8 players
'''


def available_spell_in_board_2(player_cuantity: int, promulgations: int):
    if promulgations == 2:
        spell = "Crucio"
    elif promulgations == 3:
        spell = "Imperius"
    #elif promulgations == 4 or promulgations == 5:
    #    spell = "Avada Kedavra"
    else:
        spell = ""

    return spell


'''
Get available spell string in a game with 9 or 10 players
'''


def available_spell_in_board_3(player_cuantity: int, promulgations: int):
    if promulgations == 1 or promulgations == 2:
        spell = "Crucio"
    elif promulgations == 3:
        spell = "Imperius"
    #elif promulgations == 4 or promulgations == 5:
    #    spell = "Avada Kedavra"
    else:
        spell = ""

    return spell

'''
Get available spell string
'''

@db_session()
def available_spell_in_game_conditions(game_id: int):
    board = Board[game_id]
    current_turn = get_current_turn_in_game(game_id)
    death_eater_promulgation = Board[game_id].death_eater_promulgation
    player_cuantity = Game[game_id].players.count()

    spell = ""
    if player_cuantity == 5 or player_cuantity == 6:
        spell = available_spell_in_board_1(
            player_cuantity, death_eater_promulgation)

    elif player_cuantity == 7 or player_cuantity == 8:
        spell = available_spell_in_board_2(
            player_cuantity, death_eater_promulgation)

    elif player_cuantity == 9 or player_cuantity == 10:
        spell = available_spell_in_board_3(
            player_cuantity, death_eater_promulgation)

    return spell


'''
Execute guessing
'''


@db_session()
def execute_guessing(game_id):
    game = Game[game_id]
    board = Board[game_id]
    game_deck_cuantity = len(game.card)
    cards = Card.select(
        lambda c: c.game.id == game_id and c.order > (
            game_deck_cuantity -
            3)).order_by(
        Card.order)[
                :3]

    board.spell_available = False

    return [cards[0].type, cards[1].type, cards[2].type]

'''
Execute crucio to a player in game
'''
@db_session()
def execute_crucio(game_id, player_id):
    board = Board[game_id]
    player = get_player_by_id(player_id)

    player.is_investigated = True
    board.spell_available = False

    return True if player.loyalty == "Fenix" else False
