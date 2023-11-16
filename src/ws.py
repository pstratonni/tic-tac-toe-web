import typing
from typing import Tuple, Any

from icecream import ic
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from src.game import Game


class WSGame(WebSocketEndpoint):
    encoding = 'json'
    actions = ['create', 'new', 'join', 'break']
    games = {}
    current_games = {}
    players = []

    async def cretae_game(self, ws: WebSocket) -> int:
        game = Game(ws)
        await game.get_state_init()
        self.games[id(game)] = game
        return id(game)

    async def join_game(self, ws: WebSocket, number: int) -> tuple[bool, Any]:
        game = self.games[number]
        flag = await game.join_player(ws)
        if flag:
            self.current_games[number] = self.games[number]
            del self.games[number]
            return True, self.current_games[number]
        return False, None

    async def add_player(self, ws: WebSocket):
        self.players.append(ws)

    async def delete_player(self,ws:WebSocket):
        self.players.pop(self.players.index(ws))

    async def remove_game_from_list(self, number):
        del self.games[number]

    async def remove_game_from_current(self, number):
        del self.current_games[number]

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await self.add_player(websocket)

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        if data['action'] in self.actions:
            match data['action']:
                case 'new':
                    await websocket.send_json({'action': 'new', 'games': list(self.games.keys())})

                case 'create':
                    idx = await self.cretae_game(websocket)
                    await websocket.send_json({'action': 'create', 'idx': idx})
                    await self.delete_player(websocket)
                    for ws in self.players:
                        await ws.send_json({'action': 'new', 'games': list(self.games.keys())})

                case 'join':
                    try:
                        flag, game = await self.join_game(websocket, int(data['game']))
                    except:
                        flag = False
                    if flag:
                        await self.delete_player(websocket)
                        msg = "Connection is successful"
                        ws = await game.players['player_initializing'].get_ws()
                        await websocket.send_json({'action': 'join', 'game': id(game), 'msg': msg,
                                                   'enemy_player': await game.players[
                                                       'player_initializing'].get_state(),
                                                   'player': await game.players[
                                                       'player_attached'].get_state()
                                                   })
                        await ws.send_json({'action': 'join', 'game': id(game), 'player': await game.players[
                            'player_initializing'].get_state(),
                                            'enemy_player': await game.players[
                                                'player_attached'].get_state()})
                        for ws in self.players:
                            await ws.send_json({'action': 'new', 'games': list(self.games.keys())})
                    else:
                        msg = 'Connection refused'
                        await websocket.send_json({'action': 'join', 'games': list(self.games.keys()), 'msg': msg})

                case 'break':
                    if data['joined'] == 'false':
                        await self.remove_game_from_list(int(data['game']))
                        await websocket.send_json({'action': 'break', 'games': list(self.games.keys())})
                        await self.add_player(websocket)
                    else:
                        idx = int(data['game'])
                        ws1 = await self.current_games[int(idx)].players['player_initializing'].get_ws()
                        ws2 = await self.current_games[int(idx)].players['player_attached'].get_ws()
                        await self.remove_game_from_current(idx)
                        await ws1.send_json({'action': 'break', 'games': list(self.games.keys())})
                        await ws2.send_json({'action': 'break', 'games': list(self.games.keys())})
                        await self.add_player(ws1)
                        await self.add_player(ws2)

                case _:
                    pass

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        keys = list(self.games.keys())
        for key in keys:
            if await self.games[key].players['player_initializing'].get_ws() == websocket:
                del self.games[key]
        keys = list(self.current_games.keys())
        for key in keys:
            if await self.current_games[key].players['player_initializing'].get_ws() == websocket or \
                    await self.current_games[key].players['player_attached'].get_ws() == websocket:
                del self.current_games[key]
        await self.delete_player(websocket)
