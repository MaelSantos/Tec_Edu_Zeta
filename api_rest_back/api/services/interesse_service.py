from api.repositories.interesse_repo import InteresseRepo


class InteresseService:
    
    def __init__(self):
        self.interesse_repo = InteresseRepo()