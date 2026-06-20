from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos o router que criamos
from routes.chat_route import router as chat_router
from api.util import constants

app = FastAPI(
    title=constants.API_TITLE,
    description=constants.API_DESCRIPTION,
    version=constants.API_VERSION
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

# Para rodar o servidor, use o comando no terminal:
# uvicorn main:app --reload