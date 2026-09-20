"""Acesso persistente aos dados da aplicação."""

from app.repositories.repositorio_documento import RepositorioDocumento
from app.repositories.repositorio_trecho import RepositorioTrecho

__all__ = ["RepositorioDocumento","RepositorioTrecho"]
