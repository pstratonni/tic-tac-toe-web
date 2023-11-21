from icecream import ic
from starlette.websockets import WebSocket
from enum import StrEnum


class State(StrEnum):
    ZERO = 'O'
    CROSS = 'X'


class Player:
    def __init__(self, ws: WebSocket, state: State = State.CROSS) -> None:
        self.__ws = ws
        self.__state = state

    async def get_state(self) -> State:
        return self.__state

    async def get_ws(self) -> WebSocket:
        return self.__ws

    async def check_ws(self, ws: WebSocket) -> bool:
        return self.__ws == ws


class Game:
    player_init: Player = None
    player_att: Player = None
    current_player: WebSocket = None
    current_player_state = State.CROSS
    active_game: bool = False

    @classmethod
    async def create(cls, ws: WebSocket):
        self = cls()
        self.player_init = await self.create_player(ws)
        self.current_player = await self.player_init.get_ws()
        return self

    # async def get_state_init(self):
    #     self.current_player = await self.player_init.get_state()

    async def create_player(self, ws: WebSocket, state: State = State.CROSS) -> Player:
        return Player(ws, state)

    async def toggle_current_player(self, ws: WebSocket):
        current_player = self.player_init \
            if not await self.player_init.check_ws(ws) else \
            self.player_att
        self.current_player = await current_player.get_ws()
        self.current_player_state = await current_player.get_state()

    async def join_player(self, ws: WebSocket) -> bool:
        if not await self.player_init.check_ws(ws) and \
                self.player_att is None:
            self.player_att = await self.create_player(ws, State.ZERO)
            self.active_game = True
            return True
        else:
            return False

    async def get_players(self) -> tuple[Player, Player]:
        return self.player_init, self.player_att
