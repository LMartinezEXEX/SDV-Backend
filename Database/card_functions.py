from pony import orm
from Database.database import *
import Database.turn_functions as db_turn
import Database.game_functions as db_game
from API.Model.exceptions import invalid_card_type_exception, not_discarded_exception
import random

'''
Generate 'quantity' new cards for a game
'''


@orm.db_session
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
Return the three cards in order, and create three new cards for future turns
'''


@orm.db_session
def generate_3_cards(game_id: int):
    game = Game[game_id]
    turn_number = db_turn.get_current_turn_number_in_game(game_id)
    turn = db_turn.get_turn_in_game(game_id, turn_number)
    game_deck_cuantity = len(game.card)

    cards = Card.select(
        lambda c: c.game.id == game_id and c.order > (game_deck_cuantity - 3)
        ).order_by(Card.order)[:3]

    generate_card(3, game_deck_cuantity + 1, game_id)

    turn.taken_cards = True
    return [cards[0].type, cards[1].type, cards[2].type]

'''
Get cards not discarded from the deck for the director
'''


@orm.db_session
def get_not_discarded_cards(game_id: int):
    game = db_game.get_game_by_id(game_id=game_id)
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


@orm.db_session
def discard_card(game_id: int, data: int):
    game = db_game.get_game_by_id(game_id=game_id)
    deck_quantity = len(game.card)
    card = Card.select(
        lambda c: (c.game.id == game_id) and (c.order > (deck_quantity - 6)) and (c.type == data)
        ).order_by(Card.order).first()
    if not card:
        raise invalid_card_type_exception
    card.discarded = True
    if not card.discarded:
        raise not_discarded_exception

    turn_number = db_turn.get_current_turn_number_in_game(game_id=game_id)
    turn = db_turn.get_turn_in_game(game_id=game_id, turn_number=turn_number)
    turn.pass_cards=True

    return {"message": "Card discarded"}
