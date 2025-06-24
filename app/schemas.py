from pydantic import BaseModel, EmailStr
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str   

class UserRead(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True
    
class LocationCreate(BaseModel):
    latitude: float
    longitude: float

class LocationRead(BaseModel):
    id: int
    user_id: int
    latitude: float
    longitude: float
    timestamp: datetime

    class Config:
        orm_mode = True