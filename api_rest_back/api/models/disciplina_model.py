from enum import Enum
from sqlalchemy import Column, Enum as SQLAEnum, Integer, String
from sqlalchemy.orm import relationship

from api.models.base import Base
from api.utils.enums import TipoDificuldade


class NomesDisciplinas(Enum):
    PORTUGUES = "Português"
    MATEMATICA = "Matemática"
    CIENCIAS = "Ciências"
    HISTORIA = "História"
    GEOGRAFIA = "Geografia"
    ARTES = "Artes"
    INGLES = "Inglês"
    EDUCACAO_FISICA = "Educação física"
    TEMAS_INTERDISCIPLINARES = "Temas interdisciplinares e projetos escolares"


class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    dificuldade = Column(SQLAEnum(TipoDificuldade, native_enum=False), nullable=False)

    alunos = relationship("Aluno", secondary="aluno_disciplina", back_populates="disciplinas")
    conteudos = relationship("Conteudo", back_populates="disciplina")
    desempenhos = relationship("Desempenho", back_populates="disciplina")
