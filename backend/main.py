from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from schemas import Token, UserRegister, UserResponse, RezeptCreate, RezeptResponse, BewertungCreate, BewertungResponse
from models import User, Kochrezepte, Bewertung, Favorit
from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import joinedload


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



@app.get("/rezepte", response_model=list[RezeptResponse])
def get_rezepte(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    rezepte = db.query(Kochrezepte).options(joinedload(Kochrezepte.bewertungen)).filter(Kochrezepte.username == current_username).all()
    return [rezept_mit_bewertung(r) for r in rezepte]


def rezept_mit_bewertung(rezept):
    bewertungen = rezept.bewertungen
    anzahl = len(bewertungen)
    durchschnitt = round(sum(b.sterne for b in bewertungen) / anzahl, 1) if anzahl > 0 else 0.0
    return {
        "id": rezept.id,
        "Kochrezept_Name": rezept.Kochrezept_Name,
        "kategorie": rezept.kategorie,
        "zeit": rezept.zeit,
        "zutaten": rezept.zutaten,
        "description": rezept.description,
        "image_url": rezept.image_url,
        "is_public": rezept.is_public,
        "durchschnitt": durchschnitt,
        "anzahl_bewertungen": anzahl,
        "username": rezept.username
    }

@app.get("/startseite", response_model=list[RezeptResponse])
def get_oeffentliche_rezepte(db: Session = Depends(get_db)):
    rezepte = db.query(Kochrezepte).options(joinedload(Kochrezepte.bewertungen)).filter(Kochrezepte.is_public == True).all()
    return [rezept_mit_bewertung(r) for r in rezepte]


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
    return rezept_mit_bewertung(rezept)

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
    return rezept_mit_bewertung(rezept)

@app.post("/rezepte/{rezept_id}/bewertung", response_model=BewertungResponse)
def bewerte_rezept(
    rezept_id: int,
    data: BewertungCreate,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    if not 1 <= data.sterne <= 5:
        raise HTTPException(status_code=400, detail="Sterne müssen zwischen 1 und 5 liegen")
    rezept = db.query(Kochrezepte).filter(Kochrezepte.id == rezept_id).first()
    if not rezept:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    if rezept.username == current_username:
        raise HTTPException(status_code=400, detail="Eigene Rezepte können nicht bewertet werden")
    bestehend = db.query(Bewertung).filter(
        Bewertung.rezept_id == rezept_id,
        Bewertung.username == current_username
    ).first()
    if bestehend:
        bestehend.sterne = data.sterne
        db.commit()
        db.refresh(bestehend)
        return bestehend
    bewertung = Bewertung(rezept_id=rezept_id, username=current_username, sterne=data.sterne)
    db.add(bewertung)
    db.commit()
    db.refresh(bewertung)
    return bewertung

@app.get("/meine-bewertungen")
def get_meine_bewertungen(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    bewertungen = db.query(Bewertung).filter(Bewertung.username == current_username).all()
    return {b.rezept_id: b.sterne for b in bewertungen}

@app.get("/meine-favoriten")
def get_meine_favoriten(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    favoriten = db.query(Favorit).filter(Favorit.username == current_username).all()
    return [f.rezept_id for f in favoriten]

@app.post("/rezepte/{rezept_id}/favorit", status_code=200)
def toggle_favorit(
    rezept_id: int,
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    bestehend = db.query(Favorit).filter(
        Favorit.rezept_id == rezept_id,
        Favorit.username == current_username
    ).first()
    if bestehend:
        db.delete(bestehend)
        db.commit()
        return {"favorit": False}
    favorit = Favorit(rezept_id=rezept_id, username=current_username)
    db.add(favorit)
    db.commit()
    return {"favorit": True}

@app.get("/favoriten-rezepte", response_model=list[RezeptResponse])
def get_favoriten_rezepte(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    favoriten = db.query(Favorit).filter(Favorit.username == current_username).all()
    rezept_ids = [f.rezept_id for f in favoriten]
    rezepte = db.query(Kochrezepte).options(joinedload(Kochrezepte.bewertungen)).filter(
        Kochrezepte.id.in_(rezept_ids)
    ).all()
    return [rezept_mit_bewertung(r) for r in rezepte]

