from openai import OpenAI

from app.core.config import obter_configuracoes


def obter_cliente_openai() -> OpenAI:
    """Cria cliente OpenAI somente quando a chave está configurada no backend."""
    chave = obter_configuracoes().chave_api_openai
    if not chave:
        raise RuntimeError("OPENAI_API_KEY não foi configurada no backend.")
    return OpenAI(api_key=chave)
