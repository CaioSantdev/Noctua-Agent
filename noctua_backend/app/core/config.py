import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Configuracoes:
    """Configurações obtidas do ambiente de execução."""

    url_banco: str
    diretorio_arquivos: str
    segredo_jwt: str | None
    expiracao_token_minutos: int
    chave_api_openai: str | None
    modelo_embedding: str
    modelo_llm: str
    tamanho_chunk: int
    sobreposicao_chunk: int
    max_trechos_recuperados: int
    limiar_similaridade: float
    max_tokens_contexto: int
    max_tokens_resposta: int
    max_paginas_pdf: int
    origens_cors: tuple[str, ...]
    url_supabase: str | None
    chave_servico_supabase: str | None
    bucket_documentos_supabase: str


def _normalizar_url_banco(url_banco: str) -> str:
    """Adapta URLs PostgreSQL genéricas para o driver psycopg instalado."""
    if url_banco.startswith("postgres://"):
        return url_banco.replace("postgres://", "postgresql+psycopg://", 1)
    if url_banco.startswith("postgresql://"):
        return url_banco.replace("postgresql://", "postgresql+psycopg://", 1)
    return url_banco


def obter_origens_cors() -> tuple[str, ...]:
    """Lê as origens permitidas sem exigir configuração de banco."""
    return tuple(
        origem.strip()
        for origem in os.getenv("ORIGENS_CORS", "http://localhost:5173").split(",")
        if origem.strip()
    )


@lru_cache
def obter_configuracoes() -> Configuracoes:
    """Obtém a configuração necessária para conectar ao PostgreSQL."""
    url_banco = os.getenv("DATABASE_URL")
    if not url_banco:
        raise RuntimeError("A variável de ambiente DATABASE_URL não foi configurada.")

    url_supabase = os.getenv("SUPABASE_URL")
    chave_servico_supabase = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if bool(url_supabase) != bool(chave_servico_supabase):
        raise RuntimeError(
            "SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY devem ser configuradas juntas."
        )

    return Configuracoes(
        url_banco=_normalizar_url_banco(url_banco),
        diretorio_arquivos=os.getenv("DIRETORIO_ARQUIVOS", "/tmp/noctua-arquivos"),
        segredo_jwt=os.getenv("JWT_SECRET"),
        expiracao_token_minutos=int(os.getenv("EXPIRACAO_TOKEN_MINUTOS", "60")),
        chave_api_openai=os.getenv("OPENAI_API_KEY"),
        modelo_embedding=os.getenv("MODELO_EMBEDDING", "text-embedding-3-small"),
        modelo_llm=os.getenv("MODELO_LLM", "gpt-4.1-mini"),
        tamanho_chunk=int(os.getenv("TAMANHO_CHUNK", "800")),
        sobreposicao_chunk=int(os.getenv("SOBREPOSICAO_CHUNK", "120")),
        max_trechos_recuperados=int(os.getenv("MAX_TRECHOS_RECUPERADOS", "5")),
        limiar_similaridade=float(os.getenv("LIMIAR_SIMILARIDADE", "0.30")),
        max_tokens_contexto=int(os.getenv("MAX_TOKENS_CONTEXTO", "4000")),
        max_tokens_resposta=int(os.getenv("MAX_TOKENS_RESPOSTA", "500")),
        max_paginas_pdf=int(os.getenv("MAX_PAGINAS_PDF", "5")),
        origens_cors=obter_origens_cors(),
        url_supabase=url_supabase,
        chave_servico_supabase=chave_servico_supabase,
        bucket_documentos_supabase=os.getenv("SUPABASE_BUCKET_DOCUMENTOS", "documentos"),
    )
