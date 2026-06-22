from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from api.models.base import Base


class Interesse(Base):
    __tablename__ = "interesses"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    exemplo = Column(String(255), nullable=True)

    alunos = relationship("Aluno", secondary="aluno_interesse", back_populates="interesses")
