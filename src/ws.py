import typing
from typing import Tuple, Any

from icecream import ic
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from src.game import Game


class WSGame(WebSocketEndpoint):
    encoding = 'json'
    actions = ['create', 'new', 'join', 'break', 'move']
    games = {}
    current_games = {}
    users = []

    async def cretae_game(self, ws: WebSocket):
        game = await Game.create(ws)
        self.games[id(game)] = game
        await self.delete_player(ws)
        await ws.send_json(
            {'action': 'create', 'game': id(game), 'player': await game.player_init.get_state()})

    async def join_game(self, ws: WebSocket, number: int) -> tuple[bool, int | None]:
        game = self.games[number]
        flag = await game.join_player(ws)
        if flag:
            self.current_games[number] = self.games[number]
            del self.games[number]
            await self.delete_player(ws)
            return True, number
        return False, None

    async def start_game(self, ws_atta: WebSocket, number: int):
        ws_init = await self.current_games[number].player_init.get_ws()
        msg = "Connection is successful"
        await ws_atta.send_json({'action': 'join', 'game': number, 'msg': msg,
                                 'enemy_player': await self.current_games[number].player_init.get_state(),
                                 'player': await self.current_games[number].player_att.get_state(),
                                 'active': False})
        await ws_init.send_json({'action': 'join', 'game': number,
                                 'player': await self.current_games[number].player_init.get_state(),
                                 'enemy_player': await self.current_games[number].player_att.get_state(),
                                 'active': True})


    async def check_game(self, ws: WebSocket, number: int) -> bool:
        game = self.current_games[number]
        if await game.player_init.check_ws(ws) or await game.player_att.check_ws(ws):
            return True

    async def add_player(self, ws: WebSocket):
        self.users.append(ws)
        await ws.send_json({'action': 'new', 'games': list(self.games.keys())})

    async def delete_player(self, ws: WebSocket):
        self.users.remove(ws)

    async def remove_game_from_list(self, number, ws: WebSocket):
        del self.games[number]
        await self.add_player(ws)

    async def remove_game_from_current(self, number, ws1: WebSocket, ws2: WebSocket):
        del self.current_games[number]
        await self.add_player(ws1)
        await self.add_player(ws2)

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:

        if data['action'] in self.actions:
            match data['action']:
                case 'new':
                    await self.add_player(websocket)
                case 'create':
                    await self.cretae_game(websocket)
                    for ws in self.users:
                        await ws.send_json({'action': 'new', 'games': list(self.games.keys())})

                case 'join':
                    flag, game = await self.join_game(websocket, int(data['game']))
                    if flag:
                        await self.start_game(websocket, game)
                        for ws_other in self.users:
                            await ws_other.send_json({'action': 'new', 'games': list(self.games.keys())})
                    else:
                        msg = 'Connection refused'
                        await websocket.send_json({'action': 'new', 'games': list(self.games.keys()), 'msg': msg})

                case 'move':
                    number = int(data['game'])
                    if not await self.check_game(websocket, number):
                        await websocket.send_json({'action': 'err', 'msg': 'Not your game'})
                        return

                    game = self.current_games[number]
                    if game.current_player != websocket:
                        await websocket.send_json({'action': 'err', 'msg': 'Not your move'})
                        return

                    if not await game.check_cell_availability(data['cell']):
                        await websocket.send_json({'action': 'err', 'msg': "Cell isn't available"})
                        return
                    await game.move(data['cell'])

                    players = await game.get_players()
                    if game.steps > 4:
                        is_win, line = await game.check_winner()
                        if is_win:
                            for player in players:
                                ws = await player.get_ws()
                                await ws.send_json({'action': 'win', 'winner': game.current_player_state,
                                                    'line': line, 'field': game.field})
                            return

                    if await game.check_draw():
                        for player in players:
                            ws = await player.get_ws()
                            await ws.send_json({'action': 'draw', 'field': game.field})
                        return

                    await game.toggle_current_player(websocket)
                    for player in players:
                        ws = await player.get_ws()
                        await ws.send_json(
                            {'action': 'move', 'active': True if game.current_player == ws else False,
                             'field': game.field, 'cell': data['cell']})

                case 'break':
                    if data['joined'] == 'false':
                        await self.remove_game_from_list(int(data['game']), websocket)
                        for ws in self.users:
                            await ws.send_json({'action': 'new', 'games': list(self.games.keys())})
                    else:
                        idx = int(data['game'])
                        ws1 = await self.current_games[int(idx)].player_init.get_ws()
                        ws2 = await self.current_games[int(idx)].player_att.get_ws()
                        await self.remove_game_from_current(idx, ws1, ws2)
                        await ws1.send_json({'action': 'break', 'games': list(self.games.keys())})
                        await ws2.send_json({'action': 'break', 'games': list(self.games.keys())})

                case _:
                    pass

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        try:
            await self.delete_player(websocket)
            return
        except:
            pass

        keys = list(self.games.keys())
        for key in keys:
            if await self.games[key].player_init.check_ws(websocket):
                del self.games[key]
                for ws in self.users:
                    await ws.send_json({'action': 'new', 'games': list(self.games.keys())})
                return

        keys = list(self.current_games.keys())
        for key in keys:
            ws1 = await self.current_games[key].player_init.get_ws()
            ws2 = await self.current_games[key].player_att.get_ws()
            if ws1 == websocket or ws2 == websocket:
                del self.current_games[key]
                ws = ws1 if websocket == ws2 else ws2
                await self.add_player(ws)
                return
