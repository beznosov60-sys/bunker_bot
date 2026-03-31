from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(700), nullable=False)
    severity: Mapped[float] = mapped_column(Float, nullable=False)
    surface_survival_days: Mapped[int] = mapped_column(Integer, nullable=False)


class Bunker(Base):
    __tablename__ = "bunkers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    food_months: Mapped[int] = mapped_column(Integer, nullable=False)
    water_months: Mapped[int] = mapped_column(Integer, nullable=False)
    medicine_level: Mapped[int] = mapped_column(Integer, nullable=False)
    energy_type: Mapped[str] = mapped_column(String(100), nullable=False)
    integrity: Mapped[float] = mapped_column(Float, nullable=False)


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(32), default="lobby", nullable=False)
    scenario_id: Mapped[int | None] = mapped_column(ForeignKey("scenarios.id"), nullable=True)
    bunker_id: Mapped[int | None] = mapped_column(ForeignKey("bunkers.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    scenario: Mapped[Scenario | None] = relationship()
    bunker: Mapped[Bunker | None] = relationship()
    players: Mapped[List["Player"]] = relationship(back_populates="game")
