from pony import orm
from Database.database import *
import Database.aux_functions as aux
import Database.card_functions as db_card
import Database.game_functions as db_game
import Database.player_functions as db_player


@orm.db_session
def is_current_minister(game_id: int, player_id: int):
    '''
    Assert if player is the current minister in the current turn
    '''

    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return turn.current_minister.id == player_id


@orm.db_session
def already_selected_director_candidate(game_id):
    '''
    Assert if the director candidate was already selected in the current turn
    '''

    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return turn.candidate_minister.id != turn.candidate_director.id


@orm.db_session
def already_promulgate_in_current_turn(game_id: int):
    '''
    Assert if there was already a promulgation in the current turn
    '''

    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return turn.promulgated


@orm.db_session
def get_current_turn_number_in_game(game_id: int):
    '''
    Get cuantity of turns in the game
    '''

    game = Game[game_id]
    return len(game.turn)


@orm.db_session
def get_turn_in_game(game_id: int, turn_number: int):
    '''
    Get some turn instance in the game depending the number
    '''

    return Turn.get(lambda t: t.game.id ==
                    game_id and t.turn_number == turn_number)


@orm.db_session
def get_next_candidate(players: Set(Player), last_candidate: Player = None):
    '''
    Get the next candidate for minister based on players turns and state
    '''

    next_candidate = None

    if last_candidate:
        next_candidate = players.select(
            lambda p: p.is_alive and p.turn > last_candidate.turn).order_by(
            Player.turn).first()

    if next_candidate is None:
        next_candidate = players.select(
            lambda p: p.is_alive).order_by(
            Player.turn).first()

    return next_candidate


@orm.db_session
def generate_turn(game_instance: Game, turn_number: int, candidate_minister: Player,
                  candidate_director: Player, current_minister: Player, current_director: Player,
                  last_minister: Player = None, last_director: Player = None):
    '''
    Generate a new turn with its Vote instance
    '''

    turn = Turn(game=game_instance,
                turn_number=turn_number,
                current_minister=current_minister,
                current_director=current_director,
                last_minister=last_minister if last_minister else candidate_minister,
                last_director=last_director if last_director else candidate_director,
                candidate_minister=candidate_minister,
                candidate_director=candidate_director,
                taken_cards=False,
                pass_cards=False,
                reject_notified=[],
                promulgated=False,
                imperius_player_id=0,
                expelliarmus=False,
                minister_consent=2)


    Vote(result=False,
         turn=turn)


@orm.db_session
def select_MM_candidate(game_id: int):
    '''
    Start a new turn and return the candidate for minister in mentioned turn.
    '''

    game = Game[game_id]
    players_set = game.players
    next_candidate_minister = None

    # Last turn info
    game_turns = get_current_turn_number_in_game(game_id)
    last_turn = get_turn_in_game(game_id=game_id, turn_number=game_turns)

    last_candidate_minister = last_turn.candidate_minister

    # Get LAST minister candidate
    if game_turns > 1:
        # Second last turn info
        second_last_turn = get_turn_in_game(game_id=game_id, turn_number=game_turns-1)
        if second_last_turn.imperius_player_id != 0:
            last_candidate_minister = second_last_turn.candidate_minister

    # Get NEXT minister candidate
    if last_turn.imperius_player_id != 0:
        next_candidate_minister = db_player.get_player_by_id(last_turn.imperius_player_id)
    else:
        next_candidate_minister = get_next_candidate(players_set, last_candidate_minister)

    turn = generate_turn(
        game_instance=game,
        turn_number=game_turns + 1,
        candidate_minister=next_candidate_minister,
        candidate_director=next_candidate_minister,
        last_minister=last_turn.current_minister,
        last_director=last_turn.current_director,
        current_minister=next_candidate_minister,
        current_director=next_candidate_minister)

    return next_candidate_minister.id


@orm.db_session
def create_director_candidates_list(game_id, players, previous_formula_vote):
    '''
    Create a list of suitable player ids for director candidate
    '''

    if not previous_formula_vote:
        return aux.create_players_id_list(players)

    alive_players_counter = db_game.alive_players_count(game_id)
    previous_accepted_formula_turn = previous_formula_vote.turn

    previous_director_id = previous_accepted_formula_turn.current_director.id
    previous_minister_id = previous_accepted_formula_turn.current_minister.id

    player_ids = []
    for player in players:
        if alive_players_counter <= 5 and player.id != previous_director_id:
            player_ids.append(player.id)

        elif player.id != previous_minister_id and player.id != previous_director_id:
            player_ids.append(player.id)

    return player_ids


@orm.db_session
def director_available_candidates(game_id):
    '''
    Get a list of player ids suitable for director candidate
    '''

    current_turn_number = get_current_turn_number_in_game(game_id)
    current_turn = get_turn_in_game(game_id, current_turn_number)

    regular_alive_players = Player.select(
        lambda p: p.is_alive and p.game_in.id == game_id and p.id != current_turn.candidate_minister.id)[:]

    previous_accepted_formula = Vote.select(
        lambda v: v.result and v.turn.turn_number < current_turn_number and v.turn.game.id == game_id).order_by(
        desc(
            Vote.turn)).first()

    game = Game[game_id]
    if game.chaos:
        # Hogwarts fell into chaos, so all alive players can be headmasters in current turn
        # but not current minister
        game.chaos = False
        return aux.create_players_id_list(regular_alive_players)

    return create_director_candidates_list(
        game_id, regular_alive_players, previous_accepted_formula)


@orm.db_session
def select_DD_candidate(game_id, player_id):
    '''
    Set a player as director candidate in current turn.
    This function doesn't make checks, it should've been made privously
    '''

    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    director_candidate_player = db_player.get_player_by_id(player_id)

    turn.candidate_director = director_candidate_player

    return [turn.candidate_minister.id, director_candidate_player.id]


@orm.db_session
def taked_cards(game_id: int):
    '''
    Assert if the three cards for legislative session have been taken
    '''

    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    return turn.taken_cards


@orm.db_session
def director_cards_set(game_id: int):
    '''
    Check if minister passed cards to director
    '''

    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    return turn.pass_cards


@orm.db_session
def create_first_turn(game_id: int):
    '''
    Generate first turn when game starts and therefore isnt a last minister or director
    '''

    game = db_game.get_game_by_id(game_id=game_id)
    players_set = db_game.get_player_set(game_id=game_id)
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
    db_card.generate_card(3,1,game_id)
    db_game.set_game_init(game_id)
    return next_minister.id


@orm.db_session
def get_current_minister(game_id: int):
    '''
    Get minister id in current turn
    '''

    game = db_game.get_game_by_id(game_id=game_id)
    turn_number = get_current_turn_number_in_game(game_id=game_id)
    turn = get_turn_in_game(game_id=game_id, turn_number=turn_number)
    return turn.current_minister.id


@orm.db_session
def get_current_director(game_id: int):
    '''
    Get director id in current turn
    '''

    game = db_game.get_game_by_id(game_id=game_id)
    turn_number = get_current_turn_number_in_game(game_id=game_id)
    turn = get_turn_in_game(game_id=game_id, turn_number=turn_number)
    return turn.current_director.id


@orm.db_session
def get_candidates(game_id: int):
    '''
    Get current turn's formula
    '''

    turn_number = get_current_turn_number_in_game(game_id=game_id)
    turn = get_turn_in_game(game_id=game_id, turn_number=turn_number)
    return (turn.candidate_minister.id, turn.candidate_director.id)


@orm.db_session
def is_current_director(game_id: int, player_id: int):
    '''
    Assert if a player is the current director
    '''

    turn_number = get_current_turn_number_in_game(game_id=game_id)
    turn = get_turn_in_game(game_id=game_id, turn_number=turn_number)
    return turn.current_director.id == player_id


@orm.db_session
def get_current_turn_in_game(game_id: int):
    '''
    Get current turn in game
    '''

    turn_number = get_current_turn_number_in_game(game_id)

    return get_turn_in_game(game_id, turn_number)


@orm.db_session
def is_expelliarmus_set(game_id: int):
    '''
    Asseert if current turn in expelliarmus state
    '''

    turn = get_current_turn_in_game(game_id)

    return turn.expelliarmus


@orm.db_session
def set_expelliarmus(game_id: int):
    '''
    Director execute expelliarmus in current turn
    '''

    turn = get_current_turn_in_game(game_id)

    turn.expelliarmus = True
    turn.minister_consent = 2

    return turn.turn_number


@orm.db_session
def already_expelliarmus_consent(game_id: int):
    '''
    Assert if the minister already given consent
    '''

    turn = get_current_turn_in_game(game_id)

    return turn.minister_consent != 2


@orm.db_session
def minister_set_expelliarmus_consent(game_id: int, consent: int):
    '''
    Minister accept/decline director's expelliarmus proposal
    '''

    game = db_game.get_game_by_id(game_id=game_id)
    game_deck_quantity = len(game.card)
    turn = get_current_turn_in_game(game_id)

    turn.minister_consent = consent
    turn.expelliarmus = False

    if not consent:
        return turn.turn_number

    director_cards = Card.select(lambda c: (c.game.id == game_id) and
                                  (c.order > (game_deck_quantity - 6)) and
                                  (c.order <= (game_deck_quantity - 3)) and
                                  (not c.discarded)).order_by(Card.order)[:2]

    director_cards[0].discarded = True
    director_cards[1].discarded = True

    return turn.turn_number


@orm.db_session
def is_minister_or_director_candidate(game_id: int, player_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return (turn.candidate_minister.id == player_id or
            turn.candidate_director.id == player_id)
