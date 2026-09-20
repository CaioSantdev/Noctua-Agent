from collections.abc import Callable
from typing import TypeVar

from openai import APIConnectionError, APITimeoutError, InternalServerError, RateLimitError
from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential

T = TypeVar("T")


class ErroOpenAiIndisponivel(RuntimeError):
    """Indica falha temporária ou indisponibilidade do provedor de IA."""


class ErroOpenAiConfiguracao(RuntimeError):
    """Indica credencial ou configuração inválida do provedor de IA."""


class ErroOpenAiRequisicao(RuntimeError):
    """Indica uma requisição inválida que não deve ser repetida."""


def erro_transitorio(erro: BaseException) -> bool:
    """Identifica falhas que podem melhorar em uma nova tentativa."""
    if isinstance(erro, RateLimitError):
        return getattr(erro, "code", None) not in {
            "insufficient_quota",
            "credit_balance_exhausted",
        }
    return isinstance(erro, (APIConnectionError, APITimeoutError, InternalServerError))


def executar_com_retry(chamada: Callable[[], T]) -> T:
    """Executa até três vezes, com espera exponencial, apenas em falhas transitórias."""
    return Retrying(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception(erro_transitorio),
        reraise=True,
    )(chamada)
