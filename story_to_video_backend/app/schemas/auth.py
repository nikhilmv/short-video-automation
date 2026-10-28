from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    gender: Optional[str] = None
    dob: Optional[str] = None
    role: Optional[str] = "Member"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] = "Member"

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Optional[str] = None
    status: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None

    class Config:
        from_attributes = True
