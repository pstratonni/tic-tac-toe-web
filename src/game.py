from icecream import ic
from starlette.websockets import WebSocket
from enum import StrEnum


class State(StrEnum):
    ZERO = 'O'
    CROSS = 'X'


class Player:
    def __init__(self, ws: WebSocket, username: str, state: State = State.CROSS) -> None:
        self.__ws = ws
        self.__state = state
        self.__username = username

    async def get_state(self) -> State:
        return self.__state

    async def get_ws(self) -> WebSocket:
        return self.__ws

    async def check_ws(self, ws: WebSocket) -> bool:
        return self.__ws == ws

    async def get_username(self) -> str:
        return self.__username


class Game:

    @classmethod
    async def create(cls, ws: WebSocket, username: str):
        self = cls()
        self.player_init = await self.create_player(ws, username)
        self.current_player = await self.player_init.get_ws()
        self.active_game = False
        self.player_att = None
        self.current_player_state = State.CROSS
        self.field_x = (
            [0, 0, 0],
            [0, 0, 0],
            [0, 0]
        )
        self.field_o = (
            [0, 0, 0],
            [0, 0, 0],
            [0, 0]
        )
        self.field = [
            ['-', '-', '-'],
            ['-', '-', '-'],
            ['-', '-', '-'],
        ]
        self.steps = 0
        return self

    # async def get_state_init(self):
    #     self.current_player = await self.player_init.get_state()

    async def create_player(self, ws: WebSocket, username: str, state: State = State.CROSS) -> Player:
        return Player(ws, username, state)

    async def toggle_current_player(self, ws: WebSocket):
        current_player = self.player_init \
            if not await self.player_init.check_ws(ws) else \
            self.player_att
        self.current_player = await current_player.get_ws()
        self.current_player_state = await current_player.get_state()

    async def join_player(self, ws: WebSocket, username: str) -> bool:
        if not await self.player_init.check_ws(ws) and \
                self.player_att is None:
            self.player_att = await self.create_player(ws, username, State.ZERO)
            self.active_game = True
            return True
        else:
            return False

    async def get_players(self) -> tuple[Player, Player]:
        return self.player_init, self.player_att

    async def check_cell_availability(self, cell: list[str, str]) -> bool:
        x = int(cell[0])
        y = int(cell[1])
        if self.field[x][y] == '-':
            self.field[x][y] = self.current_player_state
            return True
        return False

    async def move(self, cell: list[str, str]) -> None:
        x = int(cell[0])
        y = int(cell[1])
        field = self.field_x if self.current_player_state == State.CROSS else self.field_o
        field[0][x] += 1
        field[1][y] += 1
        if x == y == 1:
            field[2][0] += 1
            field[2][1] += 1
        elif x == y:
            field[2][0] += 1
        elif (x == 2 and y == 0) or (x == 0 and y == 2):
            field[2][1] += 1
        self.steps += 1
        return

    async def check_winner(self) -> tuple[bool, tuple[int, int] | None]:
        field_winner = self.field_x if self.current_player_state == State.CROSS else self.field_o
        for row in field_winner:
            if 3 in row:
                line_winner = (field_winner.index(row), row.index(3))
                return True, line_winner
        return False, None

    async def check_draw(self) -> bool:
        if self.steps == 9:
            return True
        return False
