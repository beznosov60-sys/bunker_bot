import uuid
import logging
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from game_manager import GameManager
from models import GameStateDB, PlayerDB, Room

app = FastAPI(title="Bunker Game")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
Base.metadata.create_all(bind=engine)
logger.info("SQLite initialized and tables ensured")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(Path(__file__).parent / "index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    logger.info("WebSocket connected: %s", websocket.client)

    current_room_id: Optional[str] = None
    current_player_id: Optional[str] = None

    async def push_room_update(room_id: str) -> None:
        room = GameManager.get_room(room_id)
        if room:
            await GameManager.broadcast(room, {"event": "room_update", "data": room.snapshot()})

    try:
        while True:
            message = await websocket.receive_json()
            event = message.get("event")
            data = message.get("data", {})

            if event == "create_room":
                name = data.get("name", "Игрок").strip() or "Игрок"
                room = GameManager.create_room()
                player_id = str(uuid.uuid4())
                GameManager.add_player(room, player_id, name, websocket)

                db.add(Room(id=room.id))
                db.add(PlayerDB(id=player_id, room_id=room.id, name=name, is_alive=True))
                db.add(GameStateDB(room_id=room.id, round=1, phase="lobby"))
                db.commit()

                current_room_id = room.id
                current_player_id = player_id
                await websocket.send_json({"event": "room_created", "data": {"room_id": room.id}})
                await push_room_update(room.id)

            elif event == "join_room":
                room_id = (data.get("room_id") or "").upper()
                name = data.get("name", "Игрок").strip() or "Игрок"
                if not room_id:
                    await websocket.send_json({"event": "error", "data": {"message": "Введите ID комнаты"}})
                    continue
                room = GameManager.get_room(room_id)
                if not room:
                    await websocket.send_json({"event": "error", "data": {"message": "Комната не найдена"}})
                    continue

                player_id = str(uuid.uuid4())
                GameManager.add_player(room, player_id, name, websocket)

                db.add(PlayerDB(id=player_id, room_id=room.id, name=name, is_alive=True))
                db.commit()

                current_room_id = room.id
                current_player_id = player_id
                await push_room_update(room.id)

            elif event == "start_game":
                room_id = data.get("room_id")
                room = GameManager.get_room(room_id)
                if not room:
                    await websocket.send_json({"event": "error", "data": {"message": "Комната не найдена"}})
                    continue
                if room.owner_id != current_player_id:
                    await websocket.send_json({"event": "error", "data": {"message": "Только создатель запускает игру"}})
                    continue

                await GameManager.start_game(room)
                game_state = db.get(GameStateDB, room_id)
                if game_state:
                    game_state.round = room.round
                    game_state.phase = room.phase
                    db.commit()

            elif event == "reveal_card":
                room_id = data.get("room_id")
                card_key = data.get("card")
                room = GameManager.get_room(room_id)
                if not room or not current_player_id:
                    await websocket.send_json({"event": "error", "data": {"message": "Не удалось раскрыть карту"}})
                    continue
                result = await GameManager.reveal_card(room, current_player_id, card_key)
                if not result:
                    await websocket.send_json({"event": "error", "data": {"message": "Нельзя раскрыть эту карту"}})
                await push_room_update(room_id)

            elif event == "vote":
                room_id = data.get("room_id")
                target_id = data.get("target_id")
                room = GameManager.get_room(room_id)
                if not room or not current_player_id:
                    await websocket.send_json({"event": "error", "data": {"message": "Не удалось проголосовать"}})
                    continue

                vote_result = await GameManager.vote(room, current_player_id, target_id)
                if target_id and vote_result is None and target_id not in room.players:
                    await websocket.send_json({"event": "error", "data": {"message": "Цель голосования не найдена"}})

                game_state = db.get(GameStateDB, room_id)
                if game_state:
                    game_state.round = room.round
                    game_state.phase = room.phase

                for player in room.players.values():
                    db_player = db.get(PlayerDB, player.id)
                    if db_player:
                        db_player.is_alive = player.is_alive
                db.commit()
            elif event == "kick_player":
                room_id = data.get("room_id")
                target_id = data.get("target_id")
                room = GameManager.get_room(room_id)
                if not room or not current_player_id:
                    await websocket.send_json({"event": "error", "data": {"message": "Комната не найдена"}})
                    continue
                if not GameManager.kick_player(room, current_player_id, target_id):
                    await websocket.send_json({"event": "error", "data": {"message": "Нельзя выгнать игрока"}})
                    continue

                db_player = db.get(PlayerDB, target_id)
                if db_player:
                    db.delete(db_player)
                    db.commit()
                await push_room_update(room_id)
            elif event == "rename_player":
                room_id = data.get("room_id")
                target_id = data.get("target_id")
                new_name = (data.get("new_name") or "").strip()
                room = GameManager.get_room(room_id)
                if not room or not current_player_id:
                    await websocket.send_json({"event": "error", "data": {"message": "Комната не найдена"}})
                    continue
                if not new_name:
                    await websocket.send_json({"event": "error", "data": {"message": "Введите новое имя"}})
                    continue
                if not GameManager.rename_player(room, current_player_id, target_id, new_name):
                    await websocket.send_json({"event": "error", "data": {"message": "Нельзя переименовать игрока"}})
                    continue

                db_player = db.get(PlayerDB, target_id)
                if db_player:
                    db_player.name = new_name
                    db.commit()
                await push_room_update(room_id)
            else:
                logger.warning("Unknown websocket event: %s", event)
                await websocket.send_json({"event": "error", "data": {"message": f"Неизвестное событие: {event}"}})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", websocket.client)
        if current_room_id and current_player_id:
            room = GameManager.get_room(current_room_id)
            if room:
                GameManager.remove_player(room, current_player_id)
                db_player = db.get(PlayerDB, current_player_id)
                if db_player:
                    db.delete(db_player)
                    db.commit()
                await push_room_update(current_room_id)
    except Exception:
        logger.exception("Unhandled websocket error")
