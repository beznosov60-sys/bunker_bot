from pydantic import BaseModel


class RevealCardRequest(BaseModel):
    game_id: int
    player_id: int
    card_type: str


class VoteRequest(BaseModel):
    game_id: int
    voter_id: int
    target_id: int
    round: int
