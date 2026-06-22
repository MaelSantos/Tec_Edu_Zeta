from enum import Enum
from sqlalchemy import Column, Enum as SQLAEnum, Integer, String
from sqlalchemy.orm import relationship

from api.models.base import Base


class TiposMascotes(Enum):
    CACHORRO = "Cachorro"
    GATO = "Gato"
    COELHO = "Coelho"
    ELEFANTE = "Elefante"
    CORUJA = "Coruja"


class EstadoMascote(Enum):
    FELIZ = "Feliz"
    TRISTE = "Triste"
    CONFUSO = "Confuso"
    PREOCUPADO = "Preocupado"
    CALMO = "Calmo"


class TipoLinguagemMascote(Enum):
    FORMAL = "Formal"
    INFORMAL = "Informal"
    CASUAL = "Casual"


class PersonalidadeMascote(Enum):
    NERD = "Nerd"
    AVENTUREIRO = "Aventureiro"
    CALMO = "Calmo"
    DIVERTIDO = "Divertido"


class Mascote(Base):
    __tablename__ = "mascotes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(80), nullable=False)
    personalidade = Column(SQLAEnum(PersonalidadeMascote, native_enum=False), nullable=False)
    tipo = Column(SQLAEnum(TiposMascotes, native_enum=False), nullable=False)
    estado = Column(SQLAEnum(EstadoMascote, native_enum=False), nullable=False)
    linguagem = Column(SQLAEnum(TipoLinguagemMascote, native_enum=False), nullable=False)

    alunos = relationship("Aluno", back_populates="mascote")
