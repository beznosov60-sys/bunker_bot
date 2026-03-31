from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import Game, Player, PlayerCard
from app.schemas.game import GameCreateRequest, GameJoinRequest, GameResponse, GameStartRequest, GameStateResponse
from app.schemas.player import VoteRequest
from app.services.game_service import GameService


router = APIRouter(prefix="/game", tags=["game"])


@router.post("/create", response_model=GameResponse)
async def create_game(payload: GameCreateRequest, db: AsyncSession = Depends(get_db)) -> GameResponse:
    service = GameService(db, seed=get_settings().card_seed)
    game = await service.create_game(payload.telegram_id, payload.name)
    return GameResponse(game_id=game.id, status=game.status)


@router.post("/join")
async def join_game(payload: GameJoinRequest, db: AsyncSession = Depends(get_db)) -> dict:
    service = GameService(db)
    player = await service.join_game(payload.game_id, payload.telegram_id, payload.name)
    return {"player_id": player.id, "game_id": player.game_id}


@router.post("/start", response_model=GameResponse)
async def start_game(payload: GameStartRequest, db: AsyncSession = Depends(get_db)) -> GameResponse:
    service = GameService(db, seed=get_settings().card_seed)
    game = await service.start_game(payload.game_id)
    return GameResponse(game_id=game.id, status=game.status)


@router.get("/state", response_model=GameStateResponse)
async def game_state(game_id: int, round: int = 1, db: AsyncSession = Depends(get_db)) -> GameStateResponse:
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    alive = await db.scalar(
        select(func.count(Player.id)).where(Player.game_id == game_id, Player.is_alive.is_(True))
    )
    return GameStateResponse(game_id=game.id, status=game.status, round=round, alive_players=alive or 0)


@router.get("/result")
async def game_result(game_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    alive_players = (
        await db.scalars(select(Player.id).where(Player.game_id == game_id, Player.is_alive.is_(True)))
    ).all()
    return {"game_id": game_id, "alive_players": alive_players, "winner_count": len(alive_players)}


@router.get("/survival")
async def game_survival(game_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    service = GameService(db)
    probability = await service.calculate_survival(game_id)
    return {"game_id": game_id, "survival_probability": probability}


@router.post("/vote")
async def vote(payload: VoteRequest, db: AsyncSession = Depends(get_db)) -> dict:
    service = GameService(db)
    await service.vote(payload.game_id, payload.voter_id, payload.target_id, payload.round)
    eliminated = await service.eliminate_by_round(payload.game_id, payload.round)
    return {"eliminated_player_id": eliminated}
