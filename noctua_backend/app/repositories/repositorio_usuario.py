import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class RepositorioUsuario:
    """Centraliza a persistência e consulta de usuários."""

    def __init__(self, sessao: Session) -> None:
        self.sessao = sessao

    def adicionar(self, usuario: Usuario) -> Usuario:
        """Persiste um usuário."""
        self.sessao.add(usuario)
        self.sessao.commit()
        self.sessao.refresh(usuario)
        return usuario

    def obter_por_email(self, email: str) -> Usuario | None:
        """Obtém usuário pelo e-mail normalizado."""
        return self.sessao.scalar(select(Usuario).where(Usuario.email == email))

    def obter_por_id(self, identificador: uuid.UUID) -> Usuario | None:
        """Obtém usuário pelo identificador presente no token."""
        return self.sessao.get(Usuario, identificador)
