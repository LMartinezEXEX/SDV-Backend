from fastapi import WebSocket, WebSocketDisconnect
from API.Model.game_check import *
from API.Model.exceptions import *
from Database.game_functions import *
from Database.player_functions import *

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: int, player_id: int):
        #state = get_game_state(game_id)
        #if state == -1 or not is_player_in_game_by_id(game_id, player_id):
        #    return await websocket.close(code=1015)

        await websocket.accept()
        try:
            self.active_connections[game_id].append(websocket)
        except KeyError:
            self.active_connections[game_id] = [websocket]


    def disconnect(self, websocket: WebSocket, game_id: int):
        self.active_connections[game_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, game_id: int):
        for connection in self.active_connections[game_id]:
            await connection.send_text(message)
