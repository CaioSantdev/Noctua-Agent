from openai import AuthenticationError, BadRequestError, OpenAIError

from app.core.config import obter_configuracoes
from app.infrastructure.cliente_openai import obter_cliente_openai
from app.services.resiliencia_openai import (
    ErroOpenAiConfiguracao,
    ErroOpenAiIndisponivel,
    ErroOpenAiRequisicao,
    executar_com_retry,
    erro_transitorio,
)


class ServicoEmbedding:
    """Gera embeddings com o modelo configurado da OpenAI."""

    def gerar(self, texto: str) -> list[float]:
        """Gera um embedding para texto não vazio."""
        if not texto.strip():
            raise ValueError("Não é possível gerar embedding de texto vazio.")
        try:
            resposta = executar_com_retry(
                lambda: obter_cliente_openai().embeddings.create(
                    model=obter_configuracoes().modelo_embedding, input=texto
                )
            )
        except AuthenticationError as erro:
            raise ErroOpenAiConfiguracao("A credencial da OpenAI é inválida.") from erro
        except BadRequestError as erro:
            raise ErroOpenAiRequisicao("A requisição enviada à OpenAI é inválida.") from erro
        except OpenAIError as erro:
            if erro_transitorio(erro):
                raise ErroOpenAiIndisponivel("A OpenAI está temporariamente indisponível.") from erro
            raise ErroOpenAiConfiguracao("A OpenAI não aceitou a solicitação.") from erro
        return resposta.data[0].embedding
