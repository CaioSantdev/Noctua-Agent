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


INSTRUCOES_AGENTE = """Você é o assistente de conhecimento do Noctua.
Responda somente com informações presentes no contexto fornecido.
Não use conhecimento externo, não invente fatos, páginas ou documentos.
Se o contexto não for suficiente, responda exatamente:
Não encontrei informações suficientes nos documentos disponíveis para responder essa pergunta.
Responda no mesmo idioma da pergunta."""


class ServicoLlm:
    """Gera respostas fundamentadas no contexto recuperado pelo RAG."""

    def responder(self, pergunta: str, contexto: str) -> str:
        """Solicita à LLM uma resposta baseada exclusivamente no contexto."""
        configuracoes = obter_configuracoes()
        try:
            resposta = executar_com_retry(
                lambda: obter_cliente_openai().responses.create(
                    model=configuracoes.modelo_llm,
                    instructions=INSTRUCOES_AGENTE,
                    input=f"Contexto disponível:\n{contexto}\n\nPergunta:\n{pergunta}",
                    max_output_tokens=configuracoes.max_tokens_resposta,
                    store=False,
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
        texto = resposta.output_text.strip()
        if not texto:
            raise RuntimeError("A LLM não retornou uma resposta de texto.")
        return texto
