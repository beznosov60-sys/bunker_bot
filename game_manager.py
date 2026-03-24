import random
import string
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket


PROFESSIONS = [
    "Инженер",
    "Врач",
    "Учитель",
    "Программист",
    "Повар",
    "Пилот",
    "Биолог",
    "Психолог",
]
HEALTH = [
    "Абсолютно здоров",
    "Астма",
    "Аллергия",
    "Проблемы со зрением",
    "Сильный иммунитет",
    "Хроническая мигрень",
]
PHOBIAS = [
    "Клаустрофобия",
    "Арахнофобия",
    "Аквафобия",
    "Социофобия",
    "Нет фобий",
    "Боязнь темноты",
]


@dataclass
class Player:
    id: str
    name: str
    websocket: WebSocket
    is_alive: bool = True
    cards: dict[str, str] = field(default_factory=dict)
    revealed: set[str] = field(default_factory=set)

    def public_view(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "is_alive": self.is_alive,
            "revealed": sorted(self.revealed),
        }


@dataclass
class GameRoom:
    id: str
    players: dict[str, Player] = field(default_factory=dict)
    state: str = "lobby"
    round: int = 1
    phase: str = "lobby"
    votes: dict[str, str] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        return {
            "room_id": self.id,
            "state": self.state,
            "round": self.round,
            "phase": self.phase,
            "players": [player.public_view() for player in self.players.values()],
        }


rooms: dict[str, GameRoom] = {}


class GameManager:
    @staticmethod
    def generate_room_id(length: int = 6) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            room_id = "".join(random.choices(alphabet, k=length))
            if room_id not in rooms:
                return room_id

    @staticmethod
    def create_room() -> GameRoom:
        room_id = GameManager.generate_room_id()
        room = GameRoom(id=room_id)
        rooms[room_id] = room
        return room

    @staticmethod
    def get_room(room_id: str) -> GameRoom | None:
        return rooms.get(room_id)

    @staticmethod
    def generate_cards() -> dict[str, str]:
        return {
            "profession": random.choice(PROFESSIONS),
            "health": random.choice(HEALTH),
            "phobia": random.choice(PHOBIAS),
        }

    @staticmethod
    def add_player(room: GameRoom, player_id: str, name: str, websocket: WebSocket) -> Player:
        player = Player(id=player_id, name=name, websocket=websocket, cards=GameManager.generate_cards())
        room.players[player_id] = player
        return player

    @staticmethod
    def remove_player(room: GameRoom, player_id: str) -> None:
        room.players.pop(player_id, None)
        room.votes = {k: v for k, v in room.votes.items() if k != player_id and v != player_id}
        if not room.players:
            rooms.pop(room.id, None)

    @staticmethod
    async def broadcast(room: GameRoom, message: dict[str, Any]) -> None:
        disconnected: list[str] = []
        for player in room.players.values():
            try:
                await player.websocket.send_json(message)
            except Exception:
                disconnected.append(player.id)

        for player_id in disconnected:
            GameManager.remove_player(room, player_id)

    @staticmethod
    async def start_game(room: GameRoom) -> None:
        room.state = "active"
        room.phase = "reveal"
        room.round = 1
        room.votes.clear()
        await GameManager.broadcast(room, {"event": "game_started", "data": room.snapshot()})

    @staticmethod
    async def reveal_card(room: GameRoom, player_id: str, card_key: str) -> dict[str, Any] | None:
        player = room.players.get(player_id)
        if not player or card_key not in player.cards:
            return None

        player.revealed.add(card_key)
        payload = {
            "event": "player_updated",
            "data": {
                "player_id": player_id,
                "card": card_key,
                "value": player.cards[card_key],
            },
        }
        await GameManager.broadcast(room, payload)
        return payload

    @staticmethod
    async def vote(room: GameRoom, voter_id: str, target_id: str) -> dict[str, Any] | None:
        voter = room.players.get(voter_id)
        target = room.players.get(target_id)
        if not voter or not target or not voter.is_alive or not target.is_alive:
            return None

        room.votes[voter_id] = target_id
        alive_players = [p for p in room.players.values() if p.is_alive]
        if len(room.votes) < len(alive_players):
            await GameManager.broadcast(room, {"event": "room_update", "data": room.snapshot()})
            return None

        counts = Counter(room.votes.values())
        eliminated_id, _ = counts.most_common(1)[0]
        eliminated = room.players[eliminated_id]
        eliminated.is_alive = False

        room.round += 1
        room.phase = "reveal"
        room.votes.clear()

        result_payload = {
            "event": "voting_results",
            "data": {
                "eliminated_player_id": eliminated.id,
                "eliminated_player_name": eliminated.name,
                "round": room.round,
                "phase": room.phase,
            },
        }
        await GameManager.broadcast(room, result_payload)
        await GameManager.broadcast(room, {"event": "room_update", "data": room.snapshot()})
        return result_payload
