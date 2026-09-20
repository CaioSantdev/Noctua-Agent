import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StatusDocumento(StrEnum):
    """Estados possíveis para o processamento de um documento."""

    PENDENTE = "pending"
    PROCESSANDO = "processing"
    PRONTO = "ready"
    FALHOU = "failed"


class Documento(Base):
    """Representa um arquivo enviado e o texto extraído dele."""

    __tablename__ = "documentos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organizacao_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizacoes.id"), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    extensao: Mapped[str] = mapped_column(String(10), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    caminho_arquivo: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    texto_extraido: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StatusDocumento] = mapped_column(
        Enum(
            StatusDocumento,
            name="status_documento",
            values_callable=lambda classe: [item.value for item in classe],
        ),
        nullable=False,
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
