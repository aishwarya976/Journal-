from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ─── TASK SCHEMAS ─────────────────────────────────────────────────────────────

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None
    status: str
    before_image: Optional[str] = None
    after_image: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── JOURNAL SCHEMAS ──────────────────────────────────────────────────────────

class JournalCreate(BaseModel):
    title: str
    content: Optional[str] = ""
    mood: Optional[str] = "neutral"
    tags: Optional[str] = ""


class JournalUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[str] = None


class JournalOut(BaseModel):
    id: int
    title: str
    content: Optional[str] = ""
    mood: Optional[str] = "neutral"
    tags: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
