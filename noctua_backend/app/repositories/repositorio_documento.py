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

    def listar(self) -> list[Documento]:
        """Lista documentos do mais recente para o mais antigo."""
        consulta = select(Documento).order_by(Documento.criado_em.desc())
        return list(self.sessao.scalars(consulta))

    def obter_por_id(self, identificador: uuid.UUID) -> Documento | None:
        """Obtém um documento pelo identificador."""
        return self.sessao.get(Documento, identificador)
