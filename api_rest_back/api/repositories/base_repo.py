from api.utils.exceptions import CrudException
from abc import ABCMeta
from api.repositories.database import SessionLocal

class BaseRepo(metaclass=ABCMeta):

    def __init__(self):
        self.session = SessionLocal()

    def close(self):
        self.session.close()

    def create(self, entidade):
        try:
            self.session.add(entidade)
            self.session.commit()
            self.session.refresh(entidade)
            return entidade.id
        except Exception as e:
            self.session.rollback()
            raise CrudException('Erro ao Salvar - Contatar ADM')

    def update(self):
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise CrudException('Erro ao Atualizar - Contatar ADM')

    def remove(self, entidade):
        try:
            self.session.delete(entidade)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise CrudException('Erro ao Remover - Contatar ADM')

    def get_by_id(self, entidade, id):
        try:
            entidade = self.session.query(entidade).filter(entidade.id == id).first()
            return entidade
        except Exception as e:
            raise CrudException('Erro ao Buscar - Contatar ADM')

    def get_all(self, entidade):
        try:
            results = self.session.query(entidade).all()
            return results
        except Exception as e:
            raise CrudException('Erro ao Buscar - Contatar ADM')