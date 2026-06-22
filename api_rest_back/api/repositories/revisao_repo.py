from typing import Optional, List

from api.models.revisao_model import Revisao
from api.repositories.base_repo import BaseRepo
from api.utils.exceptions import RepoException


class RevisaoRepo(BaseRepo):
    def get_by_conteudo(self, conteudo_id: int) -> List[Revisao]:
        try:
            return self.session.query(Revisao).filter(Revisao.conteudo_id == conteudo_id).all()
        except Exception:
            raise RepoException('Erro ao buscar revisoes por conteudo - Contatar ADM')
