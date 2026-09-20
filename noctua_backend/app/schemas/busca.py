import uuid

from pydantic import BaseModel, Field


class ConsultaBusca(BaseModel):
    """Pergunta usada para recuperar conhecimento indexado."""

    pergunta: str = Field(min_length=1, max_length=2_000)


class TrechoRecuperado(BaseModel):
    """Trecho recuperado pela busca semântica, sem resposta de LLM."""

    documento_id: uuid.UUID
    conteudo: str
    pagina: int | None
    similaridade: float
