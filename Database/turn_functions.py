from pony import orm
from Database.database import *
import Database.aux_functions as aux
import Database.game_functions as db_game
import Database.player_functions as db_player
import Database.card_functions as db_card


'''
Assert if player is the current minister in the current turn
'''


@orm.db_session
def is_current_minister(game_id: int, player_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return turn.current_minister.id == player_id


'''
Assert if the director candidate was already selected in the current turn
'''


@orm.db_session
def already_selected_director_candidate(game_id):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return turn.candidate_minister.id != turn.candidate_director.id


'''
Assert if there was already a promulgation in the current turn
'''


@orm.db_session
def already_promulgate_in_current_turn(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)
    return turn.promulgated


'''
Get cuantity of turns in the game
'''


@orm.db_session
def get_current_turn_number_in_game(game_id: int):
    game = Game[game_id]
    return len(game.turn)


'''
Get some turn instance in the game depending the number
'''


@orm.db_session
def get_turn_in_game(game_id: int, turn_number: int):
    return Turn.get(lambda t: t.game.id ==
                    game_id and t.turn_number == turn_number)




'''
Get the next candidate for minister based on players turns and state
'''


@orm.db_session
def get_next_candidate(players: Set(Player), last_candidate: Player = None):
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


'''
Generate a new turn with its Vote instance
'''


@orm.db_session
def generate_turn(game_instance: Game, turn_number: int, candidate_minister: Player,
                  candidate_director: Player, current_minister: Player, current_director: Player,
                  last_minister: Player = None, last_director: Player = None):
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
                imperius_player_id=0)


    Vote(result=False,
         turn=turn)


'''
Start a new turn and return the candidate for minister in mentioned turn.
If it's the first turn in the game, create three cards to keep always before
giving to the legislative session
'''


@orm.db_session
def select_MM_candidate(game_id: int):
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


'''
Create a list of suitable player ids for director candidate
'''


@orm.db_session
def create_director_candidates_list(game_id, players, previous_formula_vote):
    if not previous_formula_vote:
        return aux.create_players_id_list(players)

    alive_players_counter = db_game.alive_players_count(game_id)
    previous_accepted_formula_turn = previous_formula_vote.turn

    previous_director_id = previous_accepted_formula_turn.current_director.id
    previous_minister_id = previous_accepted_formula_turn.current_minister.id

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


@orm.db_session
def director_available_candidates(game_id):
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


'''
Set a player as director candidate in current turn.
This function doesn't make checks, it should've been made privously
'''


@orm.db_session
def select_DD_candidate(game_id, player_id):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    director_candidate_player = db_player.get_player_by_id(player_id)

    turn.candidate_director = director_candidate_player

    return [turn.candidate_minister.id, director_candidate_player.id]


'''
Assert if the three cards for legislative session have been taken
'''


@orm.db_session
def taked_cards(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    return turn.taken_cards

'''
Check if minister passed cards to director
'''

@orm.db_session
def director_cards_set(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id)
    turn = get_turn_in_game(game_id, turn_number)

    return turn.pass_cards


'''
Generate first turn when game starts and therefore isnt a last minister or director
'''


@orm.db_session
def create_first_turn(game_id: int):
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


'''
Get minister id in current turn
'''


@orm.db_session
def get_current_minister(game_id: int):
    game = db_game.get_game_by_id(game_id=game_id)
    turn_number = get_current_turn_number_in_game(game_id=game_id)
    turn = get_turn_in_game(game_id=game_id, turn_number=turn_number)
    return turn.current_minister.id


@orm.db_session
def get_candidates(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id=game_id)
    turn = get_turn_in_game(game_id=game_id, turn_number=turn_number)
    return (turn.candidate_minister.id, turn.candidate_director.id)


'''
Assert if a player is the current director
'''

@orm.db_session
def is_current_director(game_id: int, player_id: int):
    turn_number = get_current_turn_number_in_game(game_id=game_id)
    turn = get_turn_in_game(game_id=game_id, turn_number=turn_number)
    return turn.current_director.id == player_id


'''
Get current turn in game
'''

@orm.db_session
def get_current_turn_in_game(game_id: int):
    turn_number = get_current_turn_number_in_game(game_id)

    return get_turn_in_game(game_id, turn_number)
