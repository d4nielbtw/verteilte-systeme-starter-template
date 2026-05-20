import datetime
from sqlalchemy import String, ForeignKey
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

    rezepte: Mapped[list["Kochrezepte"]] = relationship(back_populates="autor")


class Kochrezepte(Base):
    __tablename__ = "Kochrezepte"

    id          : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Kochrezept_Name        : Mapped[str] = mapped_column(String(100), nullable=False)
    username    : Mapped[str] = mapped_column(String(100), ForeignKey("users.username"))
    image_url   : Mapped[str] = mapped_column(String(500), nullable=False)
    description : Mapped[str] = mapped_column(String(500), nullable=False)
    created_at  : Mapped[datetime.date] = mapped_column(server_default=func.now())
    
    autor: Mapped["User"] = relationship(back_populates="rezepte")
