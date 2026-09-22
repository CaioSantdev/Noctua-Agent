import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.documento import Documento


class RepositorioDocumento:
    """Centraliza a persistência de documentos."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def adicionar(self, documento: Documento) -> Documento:
        """Persiste um novo documento."""
        self.sessao.add(documento)
        self.sessao.commit()
        self.sessao.refresh(documento)
        return documento

    def atualizar(self, documento: Documento) -> Documento:
        """Persiste mudanças em um documento existente."""
        self.sessao.add(documento)
        self.sessao.commit()
        self.sessao.refresh(documento)
        return documento

    def listar(self, organizacao_id: uuid.UUID) -> list[Documento]:
        """Lista documentos do mais recente para o mais antigo."""
        consulta = (
            select(Documento)
            .where(Documento.organizacao_id == organizacao_id)
            .order_by(Documento.criado_em.desc())
        )
        return list(self.sessao.scalars(consulta))

    def obter_por_id(
        self, identificador: uuid.UUID, organizacao_id: uuid.UUID
    ) -> Documento | None:
        """Obtém um documento pelo identificador."""
        consulta = select(Documento).where(
            Documento.id == identificador,
            Documento.organizacao_id == organizacao_id,
        )
        return self.sessao.scalar(consulta)

    def obter_por_id_interno(self, identificador: uuid.UUID) -> Documento | None:
        """Obtém um documento para processamento interno do servidor.

        Este método não é exposto às rotas: o worker recebe somente o
        identificador produzido pela própria API e nunca dados de tenant do cliente.
        """
        return self.sessao.get(Documento, identificador)
