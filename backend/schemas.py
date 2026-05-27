from pydantic import BaseModel, EmailStr, Field, ConfigDict


# --- Auth-Schemas ---

class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email:    EmailStr
    password: str = Field(min_length=8, max_length=128)
    
class UserLogin(BaseModel):
    username: str
    password: str   
     
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"



class RezeptCreate(BaseModel):
    Kochrezept_Name: str
    kategorie: str
    zeit: str
    zutaten: str
    description: str
    image_url: str = ''

class RezeptResponse(BaseModel):
    id: int
    Kochrezept_Name: str
    kategorie: str
    zeit: str
    zutaten: str
    description: str
    image_url: str

    model_config = {"from_attributes": True}
    
class RezeptCreate(BaseModel):
    Kochrezept_Name: str
    kategorie: str
    zeit: str
    zutaten: str
    description: str
    image_url: str = ""
    is_public: bool = False

class RezeptResponse(BaseModel):
    id: int
    Kochrezept_Name: str
    kategorie: str
    zeit: str
    zutaten: str
    description: str
    image_url: str
    is_public: bool
    durchschnitt: float = 0.0
    anzahl_bewertungen: int = 0

    model_config = {"from_attributes": True}

class BewertungCreate(BaseModel):
    sterne: int

class BewertungResponse(BaseModel):
    id: int
    sterne: int
    username: str

    model_config = {"from_attributes": True}
