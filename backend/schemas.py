from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
import uuid
import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: uuid.UUID
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class ExpertBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str]
    bio: Optional[str]
    roles: Optional[List[str]]
    sectors: Optional[List[str]]
    regions: Optional[List[str]]
    languages: Optional[List[str]]
    years_experience: Optional[int]
    prior_engagements: Optional[dict]

class ExpertCreate(ExpertBase):
    pass

class ExpertOut(ExpertBase):
    id: uuid.UUID
    cv_url: Optional[str]
    embedding: Optional[list]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_active: bool

    class Config:
        orm_mode = True

class ToRBase(BaseModel):
    title: str
    description: Optional[str]
    requirements: Optional[str]

class ToRCreate(ToRBase):
    pass

class ToROut(ToRBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime.datetime
    embedding: Optional[list]

    class Config:
        orm_mode = True

class FeedbackBase(BaseModel):
    rating: int
    comments: Optional[str]

class FeedbackCreate(FeedbackBase):
    user_id: uuid.UUID
    expert_id: uuid.UUID
    tor_id: uuid.UUID

class FeedbackOut(FeedbackBase):
    id: uuid.UUID
    created_at: datetime.datetime

    class Config:
        orm_mode = True 