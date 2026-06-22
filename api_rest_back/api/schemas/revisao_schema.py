from typing import Optional
from pydantic import BaseModel


class RevisaoCreate(BaseModel):
    nome: str
    periodo: str
    conteudo_id: int

    class Config:
        from_attributes = True


class RevisaoResponse(BaseModel):
    id: int
    nome: str
    periodo: str
    conteudo_id: int

    class Config:
        from_attributes = True
