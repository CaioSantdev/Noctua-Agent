"""Tarefas executadas pelo worker Celery."""

import uuid

from app.infrastructure.banco import obter_fabrica_sessoes
from app.infrastructure.celery import aplicacao_celery
from app.models.documento import StatusDocumento
from app.repositories.repositorio_documento import RepositorioDocumento
from app.services.servico_documento import ErroProcessamentoDocumento, ServicoDocumento


@aplicacao_celery.task(name="noctua.processar_documento")
def processar_documento(identificador: str) -> None:
    """Extrai e indexa um documento sem ocupar o processo da API."""
    with obter_fabrica_sessoes()() as sessao:
        repositorio = RepositorioDocumento(sessao)
        documento = repositorio.obter_por_id_interno(uuid.UUID(identificador))
        if documento is None:
            return

        servico = ServicoDocumento(repositorio, documento.organizacao_id)
        try:
            servico.processar(documento)
        except ErroProcessamentoDocumento:
            # O serviço já persiste o estado FAILED para apresentação ao cliente.
            return
