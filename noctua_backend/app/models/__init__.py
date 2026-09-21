"""Modelos ORM do domínio."""

from app.models.documento import Documento, StatusDocumento
from app.models.organizacao import Organizacao
from app.models.trecho_documento import TrechoDocumento

__all__ = ["Documento", "Organizacao", "StatusDocumento", "TrechoDocumento"]
