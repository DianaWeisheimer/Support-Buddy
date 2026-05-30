import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from services.database_service import create_table

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s — %(message)s",
)

app = FastAPI(
    title="Support Buddy API",
    description="AI-powered backend for SAP Ariba support cases",
    version="1.0.0",
)

# Permite que o Streamlit (rodando em outra porta) chame a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria a tabela no banco se ainda não existir
create_table()

# Registra todas as rotas com o prefixo /api
app.include_router(router, prefix="/api")


@app.get("/health")
def health_check():
    """Endpoint simples para verificar se a API está no ar."""
    return {"status": "ok"}