from fastapi import HTTPException


class RepoException(Exception):

    def __init__(self, mensagem):
        super(RepoException, self).__init__(mensagem)
        
        
class RouteException(HTTPException):

    def __init__(self, mensagem):
        super(RouteException, self).__init__(mensagem)