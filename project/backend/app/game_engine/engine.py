from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable


class GameStage(StrEnum):
    LOBBY = "lobby"
    CARDS = "cards_distributed"
    GENERATED = "world_generated"
    ROUND = "round"
    FINISHED = "finished"


@dataclass
class TeamStats:
    team_balance: float
    health: float
    bunker: float
    scenario_modifier: float


class GameEngine:
    def __init__(self, seed: int = 42) -> None:
        self._random = random.Random(seed)

    def choose_random_ids(self, population: Iterable[int], amount: int) -> list[int]:
        values = list(population)
        if amount >= len(values):
            return values
        return self._random.sample(values, amount)

    @staticmethod
    def calculate_survival_probability(stats: TeamStats) -> float:
        score = (
            stats.team_balance * 0.4
            + stats.health * 0.2
            + stats.bunker * 0.25
            + stats.scenario_modifier * 0.15
        )
        return 1 / (1 + math.exp(-score))
