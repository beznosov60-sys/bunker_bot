from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Card, PlayerCard
from app.schemas.player import RevealCardRequest


router = APIRouter(prefix="/player", tags=["player"])


@router.get("/cards")
async def player_cards(player_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    rows = (
        await db.execute(
            select(Card.type, Card.value)
            .join(PlayerCard, PlayerCard.card_id == Card.id)
            .where(PlayerCard.player_id == player_id)
        )
    ).all()
    return {"player_id": player_id, "cards": [{"type": t, "value": v} for t, v in rows]}


@router.post("/reveal")
async def reveal_card(payload: RevealCardRequest, db: AsyncSession = Depends(get_db)) -> dict:
    row = (
        await db.execute(
            select(Card.value)
            .join(PlayerCard, PlayerCard.card_id == Card.id)
            .where(PlayerCard.player_id == payload.player_id, Card.type == payload.card_type)
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"game_id": payload.game_id, "player_id": payload.player_id, "card_type": payload.card_type, "value": row[0]}
