from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.game import router as game_router
from app.api.routes.player import router as player_router
from app.database import Base, AsyncSessionLocal, engine
from app.services.content_loader import seed_cards_and_scenarios


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_cards_and_scenarios(session)
    yield


app = FastAPI(title="Bunker API", lifespan=lifespan)
app.include_router(game_router)
app.include_router(player_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
