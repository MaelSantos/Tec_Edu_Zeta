from typing import Optional
from pydantic import BaseModel


class InteresseCreate(BaseModel):
    nome: str
    exemplo: Optional[str] = None

    class Config:
        from_attributes = True


class InteresseResponse(BaseModel):
    id: int
    nome: str
    exemplo: Optional[str] = None

    class Config:
        from_attributes = True
