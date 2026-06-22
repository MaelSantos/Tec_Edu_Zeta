class CrudException(Exception):

    def __init__(self, mensagem):
        super(CrudException, self).__init__(mensagem)