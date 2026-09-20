"""Esquemas de entrada e saída da API."""

from app.schemas.documento import DocumentoDetalhe, DocumentoResumo
from app.schemas.busca import ConsultaBusca, TrechoRecuperado

__all__ = ["ConsultaBusca", "DocumentoDetalhe", "DocumentoResumo", "TrechoRecuperado"]
