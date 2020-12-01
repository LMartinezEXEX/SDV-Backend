from pony import orm
from pydantic import EmailStr
from Database.database import *
import Database.turn_functions as db_turn
import Database.user_functions as db_user
import Database.game_functions as db_game
import Database.card_functions as db_card
import Database.board_functions as db_board
from API.Model.exceptions import player_is_dead_exception


@orm.db_session
def get_player_by_id(player_id: int):
    return Player.get(id=player_id)


@orm.db_session
def get_player_rol_and_loyalty(player_id: int):
    player = get_player_by_id(player_id=player_id)

    return {"Rol": player.rol, "Loyalty": player.loyalty}


@orm.db_session
def is_player_in_game_by_email(user_email: EmailStr, game_id: int):
    '''
    Check if the player is in the game with its email
    '''
    user_joining = db_user.get_user_by_email(email=user_email)
    game = db_game.get_game_by_id(game_id=game_id)
    for player in game.players:
        if player.user == user_joining:
            return 1
    return 0


@orm.db_session
def is_player_in_game_by_id(game_id: int, player_id: int):
    return Player.get(lambda p: p.game_in.id == game_id and p.id == player_id)


@orm.db_session
def is_player_the_owner(game_id: int, user_email: EmailStr):
    '''
    Check if the player is the owner of the game
    '''
    game = db_game.get_game_by_id(game_id=game_id)

    return game.owner.email == user_email


@orm.db_session
def put_new_player_in_game(user: EmailStr, game_id: int):
    '''
    Create a new player and join a game
    '''
    game = db_game.get_game_by_id(game_id=game_id)
    creator = db_user.get_user_by_email(email=user)
    new_player = Player(
        user=creator,
        is_alive=True,
        game_in=game,
        chat_enabled=True,
        is_investigated=False,
        turn=game.players.count()+1
    )
    commit()
    creator.playing_in.add(Player[new_player.id])
    game.players.add(Player[new_player.id])

    return new_player.id


@orm.db_session
def is_alive(game_id: int, player_id: int):
    '''
    Assert if player is alive
    '''

    player = Player.get(lambda p: p.game_in.id == game_id and p.id == player_id)

    return player.is_alive


@orm.db_session
def is_player_investigated(player_id: int):
    '''
    Assert if a player was investigated previously
    '''

    player = get_player_by_id(player_id)

    return player.is_investigated


@orm.db_session
def kill_player_leaving(player_id: int):
    '''
    When the player leave the game, the status of is_alive is False
    '''
    player = get_player_by_id(player_id=player_id)
    player.is_alive = False

    return "The player has been killed"


@orm.db_session
def player_voted(game_id: int, player_id: int):
    '''
    Assert if a player already voted
    '''

    game = db_game.get_game_by_id(game_id=game_id)
    player = get_player_by_id(player_id)

    turn = db_turn.get_current_turn_in_game(game_id)

    vote = Vote.get(lambda v: v.turn.turn_number ==
                    turn.turn_number and v.turn.game.id == game_id)

    return Player_vote.get(lambda pv: pv.player.id == player_id \
                            and pv.vote.turn == turn \
                            and pv.vote.turn.game.id == game_id)


@orm.db_session
def notify_with_player(game_id: int, player_id: int):
    turn = db_turn.get_current_turn_in_game(game_id)

    player = get_player_by_id(player_id)

    if player.is_alive:
        # If player has notified, don't let him do this again
        if player_id in turn.reject_notified:
            return { "notified": True }

        alive_players = db_game.alive_players_count(game_id)
        if len(turn.reject_notified) < alive_players:
            turn.reject_notified.append(player_id)

            # All players know that candidates were rejected, then go to next turn
            if len(turn.reject_notified) == alive_players:
                # But if chaos conditions are met, then fall into chaos!
                game = Game[game_id]
                board = Board[game_id]
                if board.election_counter == 2:
                    game_deck_cuantity = len(game.card)
                    # Select next card, returns a singleton list
                    card = Card.select(lambda c: c.game.id == game_id \
                                        and c.order > (game_deck_cuantity - 1) \
                                        and (not c.discarded)
                                       ).order_by(Card.order)[:1]

                    # Generate new card
                    db_card.generate_card(1, game_deck_cuantity + 1, game_id)

                    # This is not something necessary, just being consistent
                    turn.taken_cards = True

                    # With this rejection, we have a sequence of three elections
                    # where candidates were rejected
                    db_board.promulgate(game_id, card[0].type)
                    # Eliminate election constraints for director candidates
                    game.chaos = True
                else:
                    # Chaos conditions are not met, then board.election_counter < 2
                    game.chaos = False
                    board.election_counter += 1

                db_turn.select_MM_candidate(game_id)

        return { "notified": True }
    else:
        raise player_is_dead_exception


@db_session
def end_game_notify_with_player(game_id: int, player_id: int):
    game = Game[game_id]
    if game.state < 1:
        return { "game_result": "" }

    if not player_id in game.end_game_notified:
        players_count = game.players.count()
        if len(game.end_game_notified) < players_count:
            game.end_game_notified.append(player_id)
            if len(game.end_game_notified) == players_count:
                game.state = 2

    turn = db_turn.get_current_turn_in_game(game_id)

    board = Board[game_id]

    # Check who won and why
    message = ""
    if board.fenix_promulgation == 5:
        message = "La Orden del Fénix gana (5 promulgaciones)"
    elif board.death_eater_promulgation == 6:
        message = "Los Mortífagos ganan (6 promulgaciones)"
    elif board.death_eater_promulgation >= 3 \
        and turn.current_director != turn.current_minister \
        and turn.current_director.rol == "Voldemort":
        message = "Los Mortífagos ganan (Voldemort es director con 3 o más proclamaciones de los Mortífagos)"
    elif not (next(player for player in game.players if player.rol == "Voldemort").is_alive):
        message = "La Orden del Fénix gana (Voldemort está muerto)"

    return { "game_result": message }
