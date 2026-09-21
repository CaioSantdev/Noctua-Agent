import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.trecho_documento import TrechoDocumento

class RepositorioTrecho:
    """Centraliza a persistência e busca de trechos vetoriais."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def adicionar_varios(self, trechos: list[TrechoDocumento]) -> None:
        """Persiste vários trechos em uma única transação."""
        self.sessao.add_all(trechos)
        self.sessao.commit()

    def remover_por_documento(self, documento_id: uuid.UUID) -> None:
        """Remove trechos antigos antes de reprocessar um documento."""
        trechos = self.sessao.scalars(
            select(TrechoDocumento).where(TrechoDocumento.documento_id == documento_id)
        ).all()
        for trecho in trechos:
            self.sessao.delete(trecho)
        self.sessao.commit()

    def buscar_semelhantes(
        self,
        organizacao_id: uuid.UUID,
        embedding: list[float],
        limite: int,
    ) -> list[tuple[TrechoDocumento, float]]:
        """Busca os trechos mais próximos, restritos à organização."""
        distancia = TrechoDocumento.embedding.cosine_distance(embedding).label(
            "distancia"
        )

        consulta = (
            select(TrechoDocumento, distancia)
            .where(TrechoDocumento.organizacao_id == organizacao_id)
            .order_by(distancia)
            .limit(limite)
        )

        return list(self.sessao.execute(consulta).all())
