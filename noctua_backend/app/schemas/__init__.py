"""Esquemas de entrada e saída da API."""

from app.schemas.documento import DocumentoDetalhe, DocumentoResumo
from app.schemas.busca import ConsultaBusca, TrechoRecuperado
from app.schemas.chat import ConsultaChat, FonteChat, RespostaChat

__all__ = [
    "ConsultaBusca",
    "ConsultaChat",
    "DocumentoDetalhe",
    "DocumentoResumo",
    "FonteChat",
    "RespostaChat",
    "TrechoRecuperado",
]
