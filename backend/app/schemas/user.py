from typing import Optional, List
from pydantic import BaseModel, EmailStr

class UserPreferences(BaseModel):
    target_titles: List[str] = []
    preferred_locations: List[str] = []
    remote_only: bool = False
    min_salary: Optional[float] = None
    target_skills: List[str] = []

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
    preferences: Optional[UserPreferences] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
