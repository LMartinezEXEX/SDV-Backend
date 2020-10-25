from datetime import datetime
from pony.orm import *
from API.Model.gameModel import GameParams, OpResponse, JoinModel, InitGameIds
from Database.database import Player, User, Game, db


@db_session
def create_new_game(game_params: GameParams):
    creator = User.get(email=game_params.email)
    if not creator:
        return OpResponse(
            op = 0,
            message = "Cant find user"
        )
    game = Game(
                owner=creator,
                name=game_params.name, 
                creation_date=datetime.today(),
                state=0, 
                min_players=game_params.min_players, 
                max_players=game_params.max_players
                )
    player_owner = Player(
                         user=creator, 
                         is_alive=True, 
                         game=game, 
                         chat_enabled=True,
                         investigated=False
                         )
    commit()
    game.players.add(Player[player_owner.id])
    creator.playing_in.add(Player[player_owner.id])
    return game.id

@db_session
def join_game_with_ids(ids: JoinModel):
    game = Game.get(id=ids.game_id)
    if not game:
        return OpResponse(
            op = 0,
            message = "Cant find game"
        )
    if (game.max_players == game.players.count()):
        return OpResponse(
            op = 1,
            message = "The game reached the max amount of players"
        )
    if(game.state == 1 || game.state == 2):
        return OpResponse(
            op = 1,
            message = "The game have started or finished, try  with another game!"
        )
    user_joining = User.get(id=ids.user_id)
    if not user_joining:
        return OpResoponse(
            op = 0,
            message = "Cant find user"
        )
    player = Player(
                    user=user_joining, 
                    is_alive=True,
                    game=game,
                    chat_enabled=True, 
                    investigated=False
                    )
    user_joining.playing_in.add(player)
    game.players.add(player)
    return OpResoponse(
        op = 1,
        message = "Joined successful"
    )


@db_session
def init_game_with_ids(ids: InitGameIds):
    game = Game.get(id=ids.game_id)
    if not game:
        return OpResponse(
            op = 0,
            message = "Can't find game"
        )
    owner = Player.get(id=ids.player_id)
    if not owner:
        return OpResponse(
            op = 0,
            message = "Can't find player"
        )
    if (game.owner == owner.user):
        if (game.min_players <= game.players.count()):
            game.state = 1
        else:
            return OpResponse(
                op = 0,
                message = "The amount of players is less than the minimum"
            )
    else:
        # This should not happen. Only the owner have the button for init the game
        return OpResponse(
            op = 0,
            message = "You can't start the game, you're not the owner!"
        )
    return OpResponse(
        op = 1,
        message = "The Game has started"
    )

