from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.models.mascote_model import Mascote
from api.repositories.base_repo import BaseRepo
from api.utils.exceptions import RepoException


class MascoteRepo(BaseRepo):
    def get_by_nome(self, nome: str) -> Optional[Mascote]:
        try:
            return self.session.query(Mascote).filter(Mascote.nome == nome).first()
        except Exception:
            raise RepoException('Erro ao buscar mascote por nome - Contatar ADM')

    def get_with_alunos(self, mascote_id: int) -> Optional[Mascote]:
        try:
            stmt = select(Mascote).options(selectinload(Mascote.alunos)).filter_by(id=mascote_id)
            return self.session.execute(stmt).scalars().first()
        except Exception:
            raise RepoException('Erro ao buscar mascote com alunos - Contatar ADM')
