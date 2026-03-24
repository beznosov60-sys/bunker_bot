from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(6), primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    players: Mapped[list["PlayerDB"]] = relationship(
        "PlayerDB", back_populates="room", cascade="all, delete-orphan"
    )
    game_state: Mapped["GameStateDB"] = relationship(
        "GameStateDB", back_populates="room", uselist=False, cascade="all, delete-orphan"
    )


class PlayerDB(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_alive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    room: Mapped[Room] = relationship("Room", back_populates="players")


class GameStateDB(Base):
    __tablename__ = "game_state"

    room_id: Mapped[str] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    round: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    phase: Mapped[str] = mapped_column(String(32), default="lobby", nullable=False)

    room: Mapped[Room] = relationship("Room", back_populates="game_state")
