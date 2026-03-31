from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    is_alive: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped[User] = relationship()
    game: Mapped["Game"] = relationship(back_populates="players")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)


class PlayerCard(Base):
    __tablename__ = "player_cards"
    __table_args__ = (UniqueConstraint("player_id", "card_id", name="uq_player_card"),)

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), primary_key=True)


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    voter_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    target_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    round: Mapped[int] = mapped_column(Integer, nullable=False)


from app.models.game import Game  # noqa: E402,F401
