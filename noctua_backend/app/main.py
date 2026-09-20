import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.saude import roteador as roteador_saude
from app.api.routes.documentos import roteador as roteador_documentos
from app.services.servico_saude import ServicoSaude

logger = logging.getLogger(__name__)


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Verifica a disponibilidade inicial do banco sem impedir diagnósticos."""
    if not ServicoSaude().banco_disponivel():
        logger.error("O banco de dados não está disponível durante a inicialização.")

    yield

app = FastAPI(title="API Noctua", lifespan=ciclo_de_vida)
app.include_router(roteador_saude)
app.include_router(roteador_documentos)
