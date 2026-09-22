"""Interface entre os serviços de domínio e a fila de tarefas."""

import uuid

from kombu.exceptions import OperationalError


class ErroEnfileiramentoDocumento(RuntimeError):
    """Indica que não foi possível enviar o processamento à fila."""


def enfileirar_processamento_documento(identificador: uuid.UUID) -> None:
    """Envia ao worker o identificador de um documento já persistido."""
    from app.infrastructure.tarefas_documento import processar_documento

    try:
        processar_documento.delay(str(identificador))
    except OperationalError as erro:
        raise ErroEnfileiramentoDocumento(
            "A fila de processamento está indisponível. Tente novamente em instantes."
        ) from erro
