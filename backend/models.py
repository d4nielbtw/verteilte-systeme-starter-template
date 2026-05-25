import datetime
from sqlalchemy import String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func

from database import Base

class User(Base):
    __tablename__ = "users"

    id              : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username        : Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email           : Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    hashed_password : Mapped[str] = mapped_column(String(200), nullable=False)
    created_at      : Mapped[datetime.date] = mapped_column(server_default=func.now())

    rezepte    : Mapped[list["Kochrezepte"]] = relationship(back_populates="autor")
    bewertungen: Mapped[list["Bewertung"]] = relationship(back_populates="autor")


class Kochrezepte(Base):
    __tablename__ = "Kochrezepte"

    id              : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Kochrezept_Name : Mapped[str] = mapped_column(String(100), nullable=False)
    username        : Mapped[str] = mapped_column(String(100), ForeignKey("users.username"))
    image_url       : Mapped[str] = mapped_column(String(500), nullable=False, default="")
    description     : Mapped[str] = mapped_column(String(500), nullable=False)
    kategorie       : Mapped[str] = mapped_column(String(100), nullable=False)
    zeit            : Mapped[str] = mapped_column(String(50), nullable=False)
    zutaten         : Mapped[str] = mapped_column(String(1000), nullable=False)
    is_public       : Mapped[bool] = mapped_column(Boolean, default=False)
    created_at      : Mapped[datetime.date] = mapped_column(server_default=func.now())

    autor      : Mapped["User"] = relationship(back_populates="rezepte")
    bewertungen: Mapped[list["Bewertung"]] = relationship(back_populates="rezept", cascade="all, delete")


class Bewertung(Base):
    __tablename__ = "bewertungen"

    id        : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rezept_id : Mapped[int] = mapped_column(ForeignKey("Kochrezepte.id"))
    username  : Mapped[str] = mapped_column(String(100), ForeignKey("users.username"))
    sterne    : Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.date] = mapped_column(server_default=func.now())

    rezept: Mapped["Kochrezepte"] = relationship(back_populates="bewertungen")
    autor : Mapped["User"] = relationship(back_populates="bewertungen")