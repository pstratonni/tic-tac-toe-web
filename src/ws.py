import typing
from typing import Tuple, Any

from icecream import ic
from sqlalchemy import update
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from config.database import database
from src.game import Game
from src.models import players as db_players


class WSGame(WebSocketEndpoint):
    encoding = 'json'
    actions = ['create', 'new', 'join', 'break', 'move', 'add_name']
    games = {}
    name_user_game = {}
    current_games = {}
    users = []

    async def create_game(self, ws: WebSocket, username: str):
        game = await Game.create(ws, username)
        self.games[id(game)] = game
        self.name_user_game[id(game)] = username
        await self.delete_player(ws)
        await ws.send_json(
            {'action': 'create', 'game': id(game), 'player': await game.player_init.get_state()})

    async def join_game(self, ws: WebSocket, number: int, username: str) -> tuple[bool, int | None]:
        game = self.games[number]
        flag = await game.join_player(ws, username)
        if flag:
            self.current_games[number] = self.games[number]
            del self.games[number]
            del self.name_user_game[number]
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

    async def add_player(self, ws: WebSocket, username: str):
        self.users.append({'ws': ws, 'username': username})
        await ws.send_json(
            {'action': 'new', 'games': list(self.games.keys()), 'name_user_game': self.name_user_game})

    async def delete_player(self, ws: WebSocket):
        for idx, player in enumerate(self.users):
            if player['ws'] == ws:
                del self.users[idx]
                return
        raise

    async def remove_game_from_list(self, number, ws: WebSocket, username: str):
        del self.games[number]
        del self.name_user_game[number]
        await self.add_player(ws, username)

    async def remove_game_from_current(self, number, ws1: WebSocket, ws2: WebSocket, username1: str, username2: str):
        del self.current_games[number]
        await self.add_player(ws1, username1)
        await self.add_player(ws2, username2)

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:

        if data['action'] in self.actions:
            match data['action']:
                case 'new':
                    await self.add_player(websocket, data['username'])
                case 'create':
                    for player in self.users:
                        if player['ws'] == websocket:
                            username = str(player['username'])
                            break
                    await self.create_game(websocket, username)
                    for player in self.users:
                        await player['ws'].send_json({'action': 'new', 'games': list(self.games.keys()),
                                                      'name_user_game': self.name_user_game})

                case 'join':
                    for player in self.users:
                        if player['ws'] == websocket:
                            username = str(player['username'])
                            break
                    flag, game = await self.join_game(websocket, int(data['game']), username)
                    if flag:
                        await self.start_game(websocket, game)
                        for players_other in self.users:
                            await players_other['ws'].send_json({'action': 'new', 'games': list(self.games.keys()),
                                                                 'name_user_game': self.name_user_game})
                    else:
                        msg = 'Connection refused'
                        await websocket.send_json({'action': 'new', 'games': list(self.games.keys()), 'msg': msg,
                                                   'name_user_game': self.name_user_game})

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
                                if await player.get_state() == game.current_player_state:
                                    username = await player.get_username()
                                    query = update(db_players).where(db_players.c.username == str(username)).values(
                                        total_games=db_players.c.total_games + 1, games_won=db_players.c.games_won + 1)
                                    await database.execute(query)
                                else:
                                    username = await player.get_username()
                                    query = update(db_players).where(db_players.c.username == str(username)).values(
                                        total_games=db_players.c.total_games + 1)
                                    await database.execute(query)
                                await ws.send_json({'action': 'win', 'winner': game.current_player_state,
                                                    'line': line, 'field': game.field})
                            return

                    if await game.check_draw():
                        for player in players:
                            ws = await player.get_ws()
                            await ws.send_json({'action': 'draw', 'field': game.field})
                            username = await player.get_username()
                            query = update(db_players).where(db_players.c.username == str(username)).values(
                                total_games=db_players.c.total_games + 1, draw=db_players.c.draw + 1)
                            await database.execute(query)
                        return

                    await game.toggle_current_player(websocket)
                    for player in players:
                        ws = await player.get_ws()
                        await ws.send_json(
                            {'action': 'move', 'active': True if game.current_player == ws else False,
                             'field': game.field, 'cell': data['cell']})

                case 'break':
                    if data['joined'] == 'false':
                        game = self.games[int(data['game'])]
                        username = await game.player_init.get_username()
                        await self.remove_game_from_list(int(data['game']), websocket, username)
                        for player in self.users:
                            await player['ws'].send_json({'action': 'new', 'games': list(self.games.keys()),
                                                          'name_user_game': self.name_user_game})
                    else:
                        idx = int(data['game'])
                        ws1 = await self.current_games[int(idx)].player_init.get_ws()
                        username1 = self.current_games[int(idx)].player_init.get_username()
                        ws2 = await self.current_games[int(idx)].player_att.get_ws()
                        username2 = await self.current_games[int(idx)].player_att.get_username()
                        await self.remove_game_from_current(idx, ws1, ws2, username1, username2)
                        await ws1.send_json({'action': 'break', 'games': list(self.games.keys()),
                                             'name_user_game': self.name_user_game})
                        await ws2.send_json({'action': 'break', 'games': list(self.games.keys()),
                                             'name_user_game': self.name_user_game})
                case 'add_name':
                    username = data['username']
                    for player in self.users:
                        if player['ws'] == websocket:
                            player['username'] = username
                            break

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
                del self.name_user_game[key]
                for player in self.users:
                    await player['ws'].send_json({'action': 'new', 'games': list(self.games.keys()),
                                                  'name_user_game': self.name_user_game})
                return

        keys = list(self.current_games.keys())
        for key in keys:
            ws1 = await self.current_games[key].player_init.get_ws()
            username1 = await self.current_games[key].player_init.get_username()
            ws2 = await self.current_games[key].player_att.get_ws()
            username2 = await self.current_games[key].player_att.get_username()
            if ws1 == websocket or ws2 == websocket:
                del self.current_games[key]
                player = {'ws': ws1, 'username': username1} if websocket == ws2 else {'ws': ws2, 'username': username2}
                await self.add_player(**player)
                return
