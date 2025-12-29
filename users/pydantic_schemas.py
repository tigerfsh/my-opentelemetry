from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[date] = None
    avatar: Optional[str] = None
    thumbnail: Optional[str] = None


class UserProfileSchema(UserProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_staff: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None


class UserSchema(UserBase):
    id: int
    date_joined: datetime
    userprofile: Optional[UserProfileSchema] = None

    class Config:
        from_attributes = True