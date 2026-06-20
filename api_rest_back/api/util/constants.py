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
DATABASE_FILE_PATH = "api_rest_back/database/estude.db"
