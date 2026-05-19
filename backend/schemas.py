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


# TODO: Fügt hier eure eigenen Schemas hinzu
# class ItemCreate(BaseModel):
#     name: str
#     price: int
#
# class ItemResponse(BaseModel):
#     id: int
#     name: str
#     price: int
#     model_config = {"from_attributes": True}
