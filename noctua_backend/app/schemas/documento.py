import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.documento import StatusDocumento


class DocumentoResumo(BaseModel):
    """Dados exibidos em listas de documentos."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome_arquivo: str
    status: StatusDocumento
    criado_em: datetime


class DocumentoDetalhe(DocumentoResumo):
    """Dados completos de um documento."""

    extensao: str
    tamanho_bytes: int
