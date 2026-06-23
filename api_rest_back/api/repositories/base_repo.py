from api.utils.exceptions import RepoException
from abc import ABCMeta
from api.repositories.database import session

class BaseRepo(metaclass=ABCMeta):

    def close(self):
        try:
            session.close()
        except Exception:
            raise RepoException('Erro ao Finalizar Seção - Contatar ADM')

    def create(self, entidade):
        try:
            session.add(entidade)
            session.commit()
            session.refresh(entidade)
            return entidade.id
        except Exception:
            session.rollback()
            raise RepoException('Erro ao Salvar - Contatar ADM')
        # finally:
        #     self.close()

    def update(self):
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise RepoException('Erro ao Atualizar - Contatar ADM')
        # finally:
        #     self.close()
            
    def remove(self, entidade):
        try:
            session.delete(entidade)
            session.commit()
        except Exception:
            session.rollback()
            raise RepoException('Erro ao Remover - Contatar ADM')
        # finally:
        #     self.close()

    def get_by_id(self, entidade, id):
        try:
            return session.query(entidade).filter(entidade.id == id).first()
        except Exception:
            raise RepoException('Erro ao Buscar - Contatar ADM')
        # finally:
        #     self.close()

    def get_all(self, entidade):
        try:
            return session.query(entidade).all()
        except Exception:
            raise RepoException('Erro ao Buscar - Contatar ADM')
        # finally:
        #     self.close()