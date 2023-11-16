from icecream import ic
from starlette.websockets import WebSocket


class Player:
    def __init__(self, ws: WebSocket, state: str = 'X') -> None:
        self.__ws = ws
        self.__state = state

    async def get_state(self):
        return self.__state

    async def get_ws(self):
        return self.__ws


class Game:
    players = {'player_initializing': None,
               'player_attached': None}
    current_player = ''
    active_game = False

    def __init__(self, ws: WebSocket):
        player = self.create_player(ws)
        self.players['player_initializing'] = player

    async def get_state_init(self):
        self.current_player = await self.players['player_initializing'].get_state()

    def create_player(self, ws: WebSocket):
        return Player(ws, 'X')

    # @classmethod
    # async def create(cls, ws: WebSocket):
    #     print(cls)
    #     self = cls()
    #     player = await self.create_player(ws)
    #     self.players.append(player)
    #     self.current_player = await player.get_state()
    #     print(len(self.players))
    #     return self

    async def join_player(self, ws: WebSocket) -> bool:
        player = Player(ws, 'O')
        if await player.get_ws() != await self.players['player_initializing'].get_ws() and \
                self.players['player_attached'] is None:
            self.players['player_attached'] = player
            self.active_game = True
            return True
        else:
            return False
