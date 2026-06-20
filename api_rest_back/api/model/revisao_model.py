from api.model.conteudo_model import Conteudo

class Revisao():
    nome: str
    periodo: str #data ou periodo do ano, por exemplo: "próxima semana" ou "ao final do semestre"
    conteudo: Conteudo