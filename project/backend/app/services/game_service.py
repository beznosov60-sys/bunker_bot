from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_engine.engine import GameEngine, TeamStats
from app.models import Bunker, Card, Game, Player, PlayerCard, Scenario, User, Vote


class GameService:
    def __init__(self, db: AsyncSession, seed: int = 42) -> None:
        self.db = db
        self.engine = GameEngine(seed=seed)

    async def _get_or_create_user(self, telegram_id: int, name: str) -> User:
        user = await self.db.scalar(select(User).where(User.telegram_id == telegram_id))
        if user:
            return user
        user = User(telegram_id=telegram_id, name=name)
        self.db.add(user)
        await self.db.flush()
        return user

    async def create_game(self, telegram_id: int, name: str) -> Game:
        user = await self._get_or_create_user(telegram_id, name)
        game = Game(status="lobby")
        self.db.add(game)
        await self.db.flush()
        self.db.add(Player(user_id=user.id, game_id=game.id, is_alive=True))
        await self.db.commit()
        await self.db.refresh(game)
        return game

    async def join_game(self, game_id: int, telegram_id: int, name: str) -> Player:
        user = await self._get_or_create_user(telegram_id, name)
        player = await self.db.scalar(select(Player).where(Player.user_id == user.id, Player.game_id == game_id))
        if player:
            return player
        player = Player(user_id=user.id, game_id=game_id, is_alive=True)
        self.db.add(player)
        await self.db.commit()
        return player

    async def start_game(self, game_id: int) -> Game:
        game = await self.db.get(Game, game_id)
        scenario = await self.db.scalar(select(Scenario).order_by(func.random()).limit(1))
        bunker = Bunker(
            size=12,
            food_months=6,
            water_months=5,
            medicine_level=7,
            energy_type="hybrid",
            integrity=0.86,
        )
        self.db.add(bunker)
        await self.db.flush()
        game.scenario_id = scenario.id if scenario else None
        game.bunker_id = bunker.id
        game.status = "cards_distributed"

        players = (await self.db.scalars(select(Player).where(Player.game_id == game_id))).all()
        card_ids = (await self.db.scalars(select(Card.id))).all()
        for player in players:
            picks = self.engine.choose_random_ids(card_ids, 4)
            for card_id in picks:
                self.db.add(PlayerCard(player_id=player.id, card_id=card_id))

        await self.db.commit()
        await self.db.refresh(game)
        return game

    async def vote(self, game_id: int, voter_id: int, target_id: int, round_number: int) -> None:
        self.db.add(Vote(game_id=game_id, voter_id=voter_id, target_id=target_id, round=round_number))
        await self.db.commit()

    async def eliminate_by_round(self, game_id: int, round_number: int) -> int | None:
        votes = (
            await self.db.scalars(select(Vote).where(Vote.game_id == game_id, Vote.round == round_number))
        ).all()
        if not votes:
            return None
        counter = Counter(v.target_id for v in votes)
        eliminated_id = counter.most_common(1)[0][0]
        player = await self.db.get(Player, eliminated_id)
        if player:
            player.is_alive = False
            await self.db.commit()
        return eliminated_id

    async def calculate_survival(self, game_id: int) -> float:
        game = await self.db.get(Game, game_id)
        players = (await self.db.scalars(select(Player).where(Player.game_id == game_id, Player.is_alive.is_(True)))).all()
        if not game or not players:
            return 0.0
        alive_count = len(players)
        team_balance = min(1.0, alive_count / 6)
        health = 0.65
        bunker_score = 0.7 if game.bunker_id else 0.3
        scenario_mod = 0.4 if game.scenario_id else 0.1

        stats = TeamStats(
            team_balance=team_balance,
            health=health,
            bunker=bunker_score,
            scenario_modifier=scenario_mod,
        )
        return self.engine.calculate_survival_probability(stats)
