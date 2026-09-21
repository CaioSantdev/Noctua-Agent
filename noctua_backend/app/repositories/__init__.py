"""Acesso persistente aos dados da aplicação."""

from app.repositories.repositorio_documento import RepositorioDocumento
from app.repositories.repositorio_organizacao import RepositorioOrganizacao
from app.repositories.repositorio_trecho import RepositorioTrecho
from app.repositories.repositorio_usuario import RepositorioUsuario

__all__ = [
    "RepositorioDocumento",
    "RepositorioOrganizacao",
    "RepositorioTrecho",
    "RepositorioUsuario",
]
