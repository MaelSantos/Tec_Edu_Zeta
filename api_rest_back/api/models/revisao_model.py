from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.models.base import Base


class Revisao(Base):
    __tablename__ = "revisoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    periodo = Column(String(120), nullable=False)
    conteudo_id = Column(Integer, ForeignKey("conteudos.id"), nullable=False)

    conteudo = relationship("Conteudo", back_populates="revisoes")
