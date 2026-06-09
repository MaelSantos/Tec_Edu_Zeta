from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos o router que criamos
from routes.chat_route import router as chat_router

app = FastAPI(
    title="Tutor de Estudos API",
    description="API para conectar o Front-end ao Agente de IA",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Mude para a URL do seu front-end em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos as rotas no app principal
app.include_router(chat_router)

# Para rodar o servidor, use o comando no terminal:
# uvicorn main:app --reload