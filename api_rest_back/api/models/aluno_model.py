from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from api.models.base import Base

aluno_interesse = Table(
    "aluno_interesse",
    Base.metadata,
    Column("aluno_id", ForeignKey("alunos.id"), primary_key=True),
    Column("interesse_id", ForeignKey("interesses.id"), primary_key=True),
)

aluno_disciplina = Table(
    "aluno_disciplina",
    Base.metadata,
    Column("aluno_id", ForeignKey("alunos.id"), primary_key=True),
    Column("disciplina_id", ForeignKey("disciplinas.id"), primary_key=True),
)


class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    apelido = Column(String(120), nullable=False)
    mascote_id = Column(Integer, ForeignKey("mascotes.id"), nullable=True)

    mascote = relationship("Mascote", back_populates="alunos")
    interesses = relationship("Interesse", secondary=aluno_interesse, back_populates="alunos")
    disciplinas = relationship("Disciplina", secondary=aluno_disciplina, back_populates="alunos")
    desempenhos = relationship("Desempenho", back_populates="aluno")
 