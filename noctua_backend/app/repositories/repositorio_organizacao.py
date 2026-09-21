from sqlalchemy.orm import Session

from app.models.organizacao import Organizacao


class RepositorioOrganizacao:
    """Centraliza a persistência de organizações."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def adicionar(self, organizacao: Organizacao) -> Organizacao:
        """Persiste uma nova organização."""
        self.sessao.add(organizacao)
        self.sessao.commit()
        self.sessao.refresh(organizacao)
        return organizacao
