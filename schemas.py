from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FormOutputSchema(BaseModel):
    id: int
    bike: Optional[str] = None
    boots: Optional[str] = None
    insoles: Optional[str] = None
    pedals: Optional[str] = None
    other_bikes: Optional[str] = None
    tool_annotation: Optional[str] = None
    sport_history: Optional[str] = None
    sport_annotation: Optional[str] = None
    client_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientOutputSchema(BaseModel):
    id: int
    full_name: str
    birth_date: str
    location: str
    phone: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageInputSchema(BaseModel):
    role: Optional[str] = None
    text: Optional[str] = None
    form_id: int


class MessageOutputSchema(BaseModel):
    id: int
    role: Optional[str] = None
    text: Optional[str] = None
    form_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
