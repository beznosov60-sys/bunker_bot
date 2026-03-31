from pydantic import BaseModel


class GameCreateRequest(BaseModel):
    telegram_id: int
    name: str


class GameJoinRequest(BaseModel):
    game_id: int
    telegram_id: int
    name: str


class GameStartRequest(BaseModel):
    game_id: int


class GameResponse(BaseModel):
    game_id: int
    status: str


class GameStateResponse(BaseModel):
    game_id: int
    status: str
    round: int
    alive_players: int
