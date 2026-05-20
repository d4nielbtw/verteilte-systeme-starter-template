from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base



class User(Base):
    """Benutzertabelle – hier könnt ihr weitere Felder ergänzen."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    created_at    = Column(DateTime, server_default=func.now())
    

# TODO: Fügt hier eure eigenen Modelle hinzu
# class Item(Base):
#     __tablename__ = "items"
#     id    = Column(Integer, primary_key=True, index=True)
#     name  = Column(String(100), nullable=False)
#     ...

class Item(Base):
    __tablename__ = "items"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)           # Beschreibung (langer Text)
    image_url   = Column(String(500), nullable=True)    # Bild als URL/Pfad
    created_at  = Column(DateTime, server_default=func.now())