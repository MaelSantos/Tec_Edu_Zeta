from sqlalchemy import Column, Enum as SQLAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.models.base import Base
from api.utils.enums import TipoDificuldade


class Conteudo(Base):
    __tablename__ = "conteudos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    descricao = Column(String(1024), nullable=True)
    dificuldade = Column(SQLAEnum(TipoDificuldade, native_enum=False), nullable=False)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)

    disciplina = relationship("Disciplina", back_populates="conteudos")
    exercicios = relationship("Exercicio", back_populates="conteudo")
    revisoes = relationship("Revisao", back_populates="conteudo")
