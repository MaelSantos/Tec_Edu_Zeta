from api.utils.exceptions import RepoException
from abc import ABCMeta
from api.repositories.database import SessionLocal

class BaseRepo(metaclass=ABCMeta):

    def __init__(self):
        self.session = SessionLocal()
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # Rollback if an exception occurred inside the context
        if exc_type is not None:
            try:
                self.session.rollback()
            except Exception:
                pass
        # Always close the session when exiting the context
        self.close()
        # Do not suppress exceptions
        return False

    def close(self):
        try:
            self.session.close()
        except Exception:
            pass

    def create(self, entidade):
        try:
            self.session.add(entidade)
            self.session.commit()
            self.session.refresh(entidade)
            return entidade.id
        except Exception:
            self.session.rollback()
            raise RepoException('Erro ao Salvar - Contatar ADM')

    def update(self):
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise RepoException('Erro ao Atualizar - Contatar ADM')

    def remove(self, entidade):
        try:
            self.session.delete(entidade)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise RepoException('Erro ao Remover - Contatar ADM')

    def get_by_id(self, entidade, id):
        try:
            return self.session.query(entidade).filter(entidade.id == id).first()
        except Exception:
            raise RepoException('Erro ao Buscar - Contatar ADM')

    def get_all(self, entidade):
        try:
            return self.session.query(entidade).all()
        except Exception:
            raise RepoException('Erro ao Buscar - Contatar ADM')