import logging
import random
import string
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)

AGE_AND_GENDER = [
    "19 лет, женщина",
    "24 года, мужчина",
    "31 год, женщина",
    "38 лет, мужчина",
    "45 лет, женщина",
    "52 года, мужчина",
    "27 лет, женщина",
    "33 года, мужчина",
    "41 год, женщина",
    "29 лет, мужчина",
]
PROFESSIONS = [
    {"name": "Инженер-строитель", "description": "Проектирует укрытия, укрепления и аварийные выходы."},
    {"name": "Врач скорой помощи", "description": "Оказывает экстренную медицинскую помощь в критических ситуациях."},
    {"name": "Учитель математики", "description": "Системно мыслит и помогает обучать детей и взрослых."},
    {"name": "Программист", "description": "Автоматизирует процессы, настраивает датчики и простые системы."},
    {"name": "Повар-кондитер", "description": "Рационально использует продукты и поддерживает мораль команды."},
    {"name": "Пилот гражданской авиации", "description": "Работает по протоколам, ориентируется и принимает решения под давлением."},
    {"name": "Биолог", "description": "Разбирается в воде, микрофлоре и базовой экологии убежища."},
    {"name": "Психолог", "description": "Снижает конфликты и поддерживает психологическую устойчивость группы."},
    {"name": "Электромеханик", "description": "Ремонтирует генераторы, вентиляцию и базовое оборудование."},
    {"name": "Агроном", "description": "Организует выращивание культур в ограниченных условиях."},
    {"name": "Фельдшер", "description": "Проводит диагностику и поддерживает работу медпоста."},
    {"name": "Химик-технолог", "description": "Работает с очисткой воды и обеззараживанием ресурсов."},
]
HEALTH = [
    {"name": "Абсолютно здоров", "description": "Не имеет хронических заболеваний и ограничений."},
    {"name": "Астма", "description": "Нуждается в ингаляторе и чистом воздухе при нагрузке."},
    {"name": "Аллергия на пыль", "description": "Требуется фильтрация воздуха и регулярная уборка."},
    {"name": "Проблемы со зрением", "description": "Без очков теряет точность и скорость работы."},
    {"name": "Сильный иммунитет", "description": "Редко болеет и легче переносит инфекции."},
    {"name": "Хроническая мигрень", "description": "В стрессовых условиях возможны приступы боли."},
    {"name": "Сахарный диабет 1 типа", "description": "Нужны инсулин и контроль уровня глюкозы."},
    {"name": "Эпилепсия", "description": "Требуется режим сна и регулярный приём препаратов."},
    {"name": "Гемофилия", "description": "Опасны травмы из-за высокого риска кровотечений."},
    {"name": "Биполярное расстройство", "description": "Нужна стабильная среда и поддержка команды."},
    {"name": "Рассеянный склероз", "description": "Возможны периоды слабости и потери координации."},
    {"name": "Хроническая болезнь почек", "description": "Требует контроля рациона и качества воды."},
]
BODY_TYPE = [
    "Атлетическое",
    "Худощавое",
    "Крепкое",
    "Среднее",
    "Полное",
    "Выносливое",
    "Гибкое",
    "Мускулистое",
]
HOBBIES = [
    "Рыбалка",
    "Походы",
    "Шахматы",
    "Музыка",
    "Кулинария",
    "Робототехника",
    "Столярное дело",
    "Радиолюбительство",
    "Садоводство",
    "Фотография",
]
BAGGAGE = [
    "Аптечка и антибиотики",
    "Набор инструментов",
    "Семена и удобрения",
    "Рация и аккумуляторы",
    "Ноутбук с офлайн-библиотекой",
    "Фильтры для воды",
    "Портативный генератор",
    "Набор для ремонта одежды",
    "Контейнеры с сухпайками",
    "Туристическая газовая горелка",
]
PHOBIAS = [
    "Клаустрофобия",
    "Арахнофобия",
    "Аквафобия",
    "Социофобия",
    "Нет выраженных фобий",
    "Боязнь темноты",
    "Боязнь крови",
    "Танатофобия",
    "Агорафобия",
    "Кинофобия",
]
FEATURES = [
    "Быстро учится новому",
    "Отлично ведёт переговоры",
    "Плохо переносит стресс",
    "Знает основы первой помощи",
    "Прирождённый лидер",
    "Умеет чинить электронику",
    "Знает несколько языков",
    "Высокая физическая выносливость",
    "Умеет организовывать людей",
    "Склонен к импровизации",
]
DISASTERS = [
    "Глобальная пандемия: мир охвачен новой мутацией вируса, медицинские системы разрушены, выход на поверхность крайне опасен.",
    "Ядерная зима: после серии ударов атмосфера насыщена пеплом, температура резко снизилась, большая часть инфраструктуры уничтожена.",
    "Падение метеорита: удар вызвал волны разрушений, пожары и токсичную пыль, поверхность нестабильна.",
    "Экологический коллапс: вода и почва отравлены, пригодные ресурсы нужно добывать и очищать вручную.",
    "Восстание ИИ: автономные системы контролируют города, любые радиосигналы и перемещения отслеживаются.",
    "Супервулкан: извержение накрыло регионы пеплом, солнечный свет ограничен, продовольствие критично сокращается.",
    "Солнечная буря: электросети выведены из строя, связь и навигация фрагментированы.",
]
BUNKERS = [
    "Подземный военный бункер на 2 года: высокий уровень защиты, строгая дисциплина и ограниченное пространство.",
    "Научный комплекс с гидропоникой: есть лаборатории и стартовая система выращивания еды, но сложная техника требует обслуживания.",
    "Старый бункер с ограниченной вентиляцией: базовая защита есть, однако фильтры изношены и требуют ремонта.",
    "Современный автономный бункер с медблоком: хорошая автоматика и медицина, но высокая зависимость от энергосистемы.",
    "Конвертированный шахтный комплекс: много места и складов, но риски обрушений и трудная логистика.",
    "Полярная станция-убежище: защищена от внешних угроз, но экстремальный холод и дефицит топлива.",
]
SURVIVAL_CONDITIONS = [
    "Ограниченный запас воды на 6 месяцев: нужно нормировать потребление и наладить очистку.",
    "Нужно восстановить связь с внешним миром: без этого невозможно найти союзников и безопасные маршруты.",
    "Ожидаются набеги выживших групп: требуется постоянная охрана и укрепление входов.",
    "Система фильтрации воздуха повреждена: ремонт критичен в первые дни, иначе риск отравления растёт.",
    "Дефицит медикаментов: любая травма и инфекция становятся стратегической угрозой для команды.",
    "Нестабильный источник питания: отключения мешают вентиляции и хранению запасов.",
    "Часть отсеков затоплена: доступ к складам ограничен и нужен план перераспределения ресурсов.",
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
    owner_id: Optional[str] = None
    state: str = "lobby"
    round: int = 1
    phase: str = "lobby"
    votes: dict[str, str] = field(default_factory=dict)
    disaster: Optional[str] = None
    bunker: Optional[str] = None
    survival_condition: Optional[str] = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "room_id": self.id,
            "owner_id": self.owner_id,
            "state": self.state,
            "round": self.round,
            "phase": self.phase,
            "disaster": self.disaster,
            "bunker": self.bunker,
            "survival_condition": self.survival_condition,
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
        logger.info("Created room %s", room_id)
        return room

    @staticmethod
    def get_room(room_id: str) -> Optional[GameRoom]:
        return rooms.get(room_id)

    @staticmethod
    def generate_cards() -> dict[str, str]:
        profession = random.choice(PROFESSIONS)
        health = random.choice(HEALTH)
        return {
            "age_gender": random.choice(AGE_AND_GENDER),
            "profession": f"{profession['name']} — {profession['description']}",
            "health": f"{health['name']} — {health['description']}",
            "body_type": random.choice(BODY_TYPE),
            "hobby": random.choice(HOBBIES),
            "baggage": random.choice(BAGGAGE),
            "phobia": random.choice(PHOBIAS),
            "feature": random.choice(FEATURES),
        }

    @staticmethod
    def add_player(room: GameRoom, player_id: str, name: str, websocket: WebSocket) -> Player:
        player = Player(id=player_id, name=name, websocket=websocket, cards=GameManager.generate_cards())
        room.players[player_id] = player
        if room.owner_id is None:
            room.owner_id = player_id
        logger.info("Player %s (%s) joined room %s", name, player_id, room.id)
        return player

    @staticmethod
    def remove_player(room: GameRoom, player_id: str) -> None:
        logger.info("Removing player %s from room %s", player_id, room.id)
        room.players.pop(player_id, None)
        room.votes = {k: v for k, v in room.votes.items() if k != player_id and v != player_id}
        if room.owner_id == player_id:
            room.owner_id = next(iter(room.players), None)
            logger.info("Room %s new owner is %s", room.id, room.owner_id)
        if not room.players:
            rooms.pop(room.id, None)
            logger.info("Deleted empty room %s", room.id)

    @staticmethod
    def delete_room(room_id: str) -> bool:
        room = rooms.get(room_id)
        if not room:
            return False
        rooms.pop(room_id, None)
        logger.info("Room %s deleted by owner", room_id)
        return True

    @staticmethod
    async def broadcast(room: GameRoom, message: dict[str, Any]) -> None:
        disconnected: list[str] = []
        for player in room.players.values():
            try:
                await player.websocket.send_json(message)
            except Exception:
                logger.exception("Failed to send message to player %s in room %s", player.id, room.id)
                disconnected.append(player.id)

        for player_id in disconnected:
            GameManager.remove_player(room, player_id)

    @staticmethod
    async def start_game(room: GameRoom) -> None:
        room.state = "active"
        room.phase = "reveal"
        room.round = 1
        room.votes.clear()
        room.disaster = random.choice(DISASTERS)
        room.bunker = random.choice(BUNKERS)
        room.survival_condition = random.choice(SURVIVAL_CONDITIONS)
        logger.info(
            "Started game in room %s: disaster=%s bunker=%s condition=%s",
            room.id,
            room.disaster,
            room.bunker,
            room.survival_condition,
        )
        await GameManager.broadcast(room, {"event": "game_started", "data": room.snapshot()})
        for player in room.players.values():
            await player.websocket.send_json(
                {
                    "event": "personal_cards",
                    "data": {
                        "room_id": room.id,
                        "cards": player.cards,
                        "revealed": sorted(player.revealed),
                    },
                }
            )

    @staticmethod
    async def reveal_card(room: GameRoom, player_id: str, card_key: str) -> Optional[dict[str, Any]]:
        player = room.players.get(player_id)
        if not player or card_key not in player.cards:
            logger.warning("Invalid reveal card request room=%s player=%s card=%s", room.id, player_id, card_key)
            return None

        if card_key in player.revealed:
            player.revealed.remove(card_key)
        else:
            player.revealed.add(card_key)

        payload = {
            "event": "player_updated",
            "data": {
                "player_id": player_id,
                "card": card_key,
                "value": player.cards[card_key],
                "is_revealed": card_key in player.revealed,
            },
        }
        await GameManager.broadcast(room, payload)
        return payload

    @staticmethod
    async def vote(room: GameRoom, voter_id: str, target_id: str) -> Optional[dict[str, Any]]:
        voter = room.players.get(voter_id)
        target = room.players.get(target_id)
        if not voter or not target or not voter.is_alive or not target.is_alive:
            logger.warning("Invalid vote room=%s voter=%s target=%s", room.id, voter_id, target_id)
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

    @staticmethod
    def rename_player(room: GameRoom, actor_id: str, target_id: str, new_name: str) -> bool:
        if room.owner_id != actor_id:
            return False
        player = room.players.get(target_id)
        if not player:
            return False
        player.name = new_name
        logger.info("Player %s renamed to %s in room %s", target_id, new_name, room.id)
        return True

    @staticmethod
    def kick_player(room: GameRoom, actor_id: str, target_id: str) -> bool:
        if room.owner_id != actor_id or actor_id == target_id or target_id not in room.players:
            return False
        GameManager.remove_player(room, target_id)
        logger.info("Player %s kicked from room %s by owner %s", target_id, room.id, actor_id)
        return True
