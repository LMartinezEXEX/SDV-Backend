from pony import orm
from Database.database import *
import Database.card_functions as db_card
import Database.turn_functions as db_turn
import Database.game_functions as db_game
import Database.player_functions as db_player


@orm.db_session
def check_available_spell(game_id: int):
    '''
    Check if with current promulgations a spell is available
    '''

    board = Board[game_id]
    death_eater_promulgation = board.death_eater_promulgation
    player_cuantity = Game[game_id].players.count()

    if (player_cuantity == 5 or player_cuantity ==
            6) and 3 <= death_eater_promulgation <= 5:
        board.spell_available = True

    elif (player_cuantity == 7 or player_cuantity == 8) and 2 <= death_eater_promulgation <= 5:
        board.spell_available = True

    elif (player_cuantity == 9 or player_cuantity == 10) and 1 <= death_eater_promulgation <= 5:

        board.spell_available = True


def available_spell_in_board_1(player_cuantity: int, promulgations: int):
    '''
    Get available spell string in a game with 5 or 6 players
    '''

    if promulgations == 3:
        spell = "Guessing"
    elif promulgations == 4 or promulgations == 5:
        spell = "Avada Kedavra"
    else:
        spell = ""

    return spell


def available_spell_in_board_2(player_cuantity: int, promulgations: int):
    '''
    Get available spell string in a game with 7 or 8 players
    '''

    if promulgations == 2:
        spell = "Crucio"
    elif promulgations == 3:
        spell = "Imperius"
    elif promulgations == 4 or promulgations == 5:
        spell = "Avada Kedavra"
    else:
        spell = ""

    return spell


def available_spell_in_board_3(player_cuantity: int, promulgations: int):
    '''
    Get available spell string in a game with 9 or 10 players
    '''

    if promulgations == 1 or promulgations == 2:
        spell = "Crucio"
    elif promulgations == 3:
        spell = "Imperius"
    elif promulgations == 4 or promulgations == 5:
        spell = "Avada Kedavra"
    else:
        spell = ""

    return spell


@orm.db_session
def available_spell_in_game_conditions(game_id: int):
    '''
    Get available spell string
    '''

    board = Board[game_id]
    death_eater_promulgation = board.death_eater_promulgation
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


@orm.db_session
def execute_guessing(game_id):
    '''
    Execute guessing
    '''

    game = db_game.get_game_by_id(game_id)
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


@orm.db_session
def execute_crucio(game_id, player_id):
    '''
    Execute crucio to a player in game
    '''

    board = Board[game_id]
    player = db_player.get_player_by_id(player_id)

    player.is_investigated = True
    board.spell_available = False

    return player.loyalty == "Fenix Order"


@orm.db_session
def execute_avada_kedavra(game_id: int, player_id: int):
    '''
    Execute avada kedavra to a player in game
    '''

    game = db_game.get_game_by_id(game_id)
    board = Board[game_id]

    player = db_player.get_player_by_id(player_id)
    player.is_alive = False
    player.chat_enabled = False

    board.spell_available = False

    return player.rol == "Voldemort"


@orm.db_session
def execute_imperius(game_id: int, player_id: int):
    '''
    Execute imperius to a player to be the next minister candidate in game
    '''

    board = Board[game_id]
    turn = db_turn.get_current_turn_in_game(game_id)

    turn.imperius_player_id = player_id
    board.spell_available = False

    return player_id
