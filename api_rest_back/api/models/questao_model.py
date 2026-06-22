from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.models.base import Base


class Questao(Base):
    __tablename__ = "questaos"

    id = Column(Integer, primary_key=True, index=True)
    enunciado = Column(String(2048), nullable=False)
    dica = Column(String(1024), nullable=True)
    resposta_correta = Column(String(1024), nullable=False)
    resposta_incorreta1 = Column(String(1024), nullable=True)
    resposta_incorreta2 = Column(String(1024), nullable=True)
    resposta_incorreta3 = Column(String(1024), nullable=True)
    resposta_incorreta4 = Column(String(1024), nullable=True)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=False)

    exercicio = relationship("Exercicio", back_populates="questoes")
