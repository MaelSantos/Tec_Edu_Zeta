from typing import Optional

from api.models.interesse_model import Interesse
from api.repositories.base_repo import BaseRepo
from api.utils.exceptions import RepoException
from api.repositories.database import session

class InteresseRepo(BaseRepo):
    def get_by_nome(self, nome: str) -> Optional[Interesse]:
        try:
            return session.query(Interesse).filter(Interesse.nome == nome).first()
        except Exception:
            raise RepoException('Erro ao buscar interesse por nome - Contatar ADM')
