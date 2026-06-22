from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.models.conteudo_model import Conteudo
from api.repositories.base_repo import BaseRepo
from api.utils.exceptions import RepoException


class ConteudoRepo(BaseRepo):
    def get_with_exercicios(self, conteudo_id: int) -> Optional[Conteudo]:
        try:
            stmt = select(Conteudo).options(selectinload(Conteudo.exercicios)).filter_by(id=conteudo_id)
            return self.session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar conteudo com exercicios - Contatar ADM')

    def get_with_revisoes(self, conteudo_id: int) -> Optional[Conteudo]:
        try:
            stmt = select(Conteudo).options(selectinload(Conteudo.revisoes)).filter_by(id=conteudo_id)
            return self.session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar conteudo com revisoes - Contatar ADM')
