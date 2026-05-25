from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from schemas import Token, UserRegister, UserResponse, RezeptCreate, RezeptResponse


from auth import (
    DUMMY_HASH,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

from database import Base, engine, get_db
from models import User, Kochrezepte
from schemas import Token, UserRegister, UserResponse

# Tabellen anlegen (falls noch nicht vorhanden)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mein Projekt", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
# Datenbank verbindung wird gecheckt
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Führt eine minimale Abfrage aus, die keine Last erzeugt
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:  
        raise HTTPException(
            status_code=503, 
            detail=f"Database connection failed: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Authentifizierung
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username bereits vergeben")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email bereits vergeben")
    
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/token", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        verify_password(form_data.password, DUMMY_HASH)
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    token = create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/my-profile", response_model=UserResponse)
def get_profile(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == current_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    return user


# ---------------------------------------------------------------------------
# TODO: Eure eigenen Endpoints hier einfügen

@app.get("/rezepte", response_model=list[RezeptResponse])
def get_rezepte(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    return db.query(Kochrezepte).filter(Kochrezepte.username == current_username).all()


@app.post("/rezepte", response_model=RezeptResponse, status_code=201)
def create_rezept(
    data: RezeptCreate,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    rezept = Kochrezepte(**data.model_dump(), username=current_username)
    db.add(rezept)
    db.commit()
    db.refresh(rezept)
    return rezept


@app.delete("/rezepte/{rezept_id}", status_code=204)
def delete_rezept(
    rezept_id: int,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    rezept = db.query(Kochrezepte).filter(
        Kochrezepte.id == rezept_id,
        Kochrezepte.username == current_username
    ).first()
    if not rezept:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    db.delete(rezept)
    db.commit()


@app.put("/rezepte/{rezept_id}", response_model=RezeptResponse)
def update_rezept(
    rezept_id: int,
    data: RezeptCreate,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    rezept = db.query(Kochrezepte).filter(
        Kochrezepte.id == rezept_id,
        Kochrezepte.username == current_username
    ).first()
    if not rezept:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    for key, value in data.model_dump().items():
        setattr(rezept, key, value)
    db.commit()
    db.refresh(rezept)
    return rezept


# ---------------------------------------------------------------------------

# Beispiel:
# @app.get("/items")
# def get_items(db: Session = Depends(get_db)):
#     return db.query(Item).all()
#
# @app.post("/items", status_code=201)
# def create_item(data: ItemCreate, db: Session = Depends(get_db)):
#     item = Item(**data.model_dump())
#     db.add(item)
#     db.commit()
#     db.refresh(item)
#     return item
