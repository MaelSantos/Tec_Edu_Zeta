from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.models.base import Base


class Exercicio(Base):
    __tablename__ = "exercicios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    dificuldade = Column(String(50), nullable=False)
    exemplo = Column(String(1024), nullable=True)
    conteudo_id = Column(Integer, ForeignKey("conteudos.id"), nullable=False)

    conteudo = relationship("Conteudo", back_populates="exercicios")
    questoes = relationship("Questao", back_populates="exercicio", cascade="all, delete-orphan")

