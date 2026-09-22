from pydantic import BaseModel, Field


class ConsultaChat(BaseModel):
    """Pergunta submetida ao agente de conhecimento."""

    question: str = Field(min_length=1, max_length=2_000)


class FonteChat(BaseModel):
    """Fonte vinculada a um chunk usado como contexto."""

    document: str
    page: int | None
    excerpt: str = Field(min_length=1, max_length=220)


class RespostaChat(BaseModel):
    """Resposta do agente acompanhada de suas fontes."""

    answer: str
    sources: list[FonteChat]
