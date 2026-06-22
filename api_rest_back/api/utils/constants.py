"""
Arquivo de constantes para a API - Tutor de Estudos
Centraliza todas as configurações e valores fixos do projeto
"""

# ===== Configurações da API =====
API_TITLE = "Tutor de Estudos API"
API_DESCRIPTION = "API para conectar o Front-end ao Agente de IA"
API_VERSION = "1.0.0"

# ===== Configurações de CORS =====
CORS_ALLOW_ORIGINS = ["*"]  # Mude para a URL do seu front-end em produção
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# ===== Configurações do Modelo de IA =====
AI_MODEL_ID = "gemini-3-flash-preview"

# ===== Configurações do Banco de Dados =====
import os
from urllib.parse import quote_plus

DATABASE_DRIVER = os.getenv("DATABASE_DRIVER", "postgresql+psycopg")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = quote_plus(os.getenv("DATABASE_PASSWORD", "postgres"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "eduzetta")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"{DATABASE_DRIVER}://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}",
)

# banco do Agno / agente IA pode usar o mesmo postgres ou outro URL separado
AGNO_DATABASE_URL = os.getenv("AGNO_DATABASE_URL", DATABASE_URL)
