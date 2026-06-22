from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.repositories.database import engine
from api.models.base import Base
from api.routers.chat_router import router as chat_router
from api.routers.aluno_router import router as aluno_router
from api.utils import constants

app = FastAPI(
    title=constants.API_TITLE,
    description=constants.API_DESCRIPTION,
    version=constants.API_VERSION,
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=constants.CORS_ALLOW_ORIGINS,
    allow_credentials=constants.CORS_ALLOW_CREDENTIALS,
    allow_methods=constants.CORS_ALLOW_METHODS,
    allow_headers=constants.CORS_ALLOW_HEADERS,
)

# Registramos as rotas no app principal
app.include_router(chat_router)
app.include_router(aluno_router)

# Cria as tabelas do banco de dados quando o aplicativo iniciar
Base.metadata.create_all(bind=engine)

# Para rodar o servidor, use o comando no terminal:
# uvicorn api.main:app --reload