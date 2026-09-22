import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.saude import roteador as roteador_saude
from app.api.routes.documentos import roteador as roteador_documentos
from app.api.routes.busca import roteador as roteador_busca
from app.api.routes.chat import roteador as roteador_chat
from app.api.routes.autenticacao import roteador as roteador_autenticacao
from app.core.config import obter_origens_cors
from app.services.servico_saude import ServicoSaude

logger = logging.getLogger(__name__)


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Verifica a disponibilidade inicial do banco sem impedir diagnósticos."""
    if not ServicoSaude().banco_disponivel():
        logger.error("O banco de dados não está disponível durante a inicialização.")

    yield

app = FastAPI(title="API Noctua", lifespan=ciclo_de_vida)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(obter_origens_cors()),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(roteador_saude)
app.include_router(roteador_documentos)
app.include_router(roteador_busca)
app.include_router(roteador_chat)
app.include_router(roteador_autenticacao)
