from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from api.models.base import Base


class Desempenho(Base):
    __tablename__ = "desempenhos"

    id = Column(Integer, primary_key=True, index=True)
    tempo_de_estudo = Column(Integer, nullable=False)
    acertos = Column(Integer, nullable=False)
    erros = Column(Integer, nullable=False)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)

    aluno = relationship("Aluno", back_populates="desempenhos")
    disciplina = relationship("Disciplina", back_populates="desempenhos")
