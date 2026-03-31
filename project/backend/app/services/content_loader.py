import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Card, Scenario


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


async def seed_cards_and_scenarios(db: AsyncSession) -> None:
    has_cards = await db.scalar(select(Card.id).limit(1))
    has_scenarios = await db.scalar(select(Scenario.id).limit(1))

    if not has_cards:
        cards_payload = json.loads((DATA_DIR / "cards.json").read_text(encoding="utf-8"))
        for card_type, values in cards_payload.items():
            for value in values:
                db.add(Card(type=card_type, value=value))

    if not has_scenarios:
        scenarios_payload = json.loads((DATA_DIR / "scenarios.json").read_text(encoding="utf-8"))
        for scenario in scenarios_payload:
            db.add(Scenario(**scenario))

    await db.commit()
