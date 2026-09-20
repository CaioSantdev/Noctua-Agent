import httpx
import pytest
from openai import APIConnectionError, RateLimitError

from app.services import resiliencia_openai
from app.services.resiliencia_openai import executar_com_retry, erro_transitorio


def _erro_limite(codigo: str) -> RateLimitError:
    """Cria erro 429 sem fazer requisição externa."""
    requisicao = httpx.Request("POST", "https://api.openai.com/v1/responses")
    resposta = httpx.Response(429, request=requisicao)
    return RateLimitError("Limite", response=resposta, body={"code": codigo})


def test_saldo_esgotado_nao_recebe_retry() -> None:
    """Evita repetir chamadas que nunca terão sucesso sem novos créditos."""
    assert not erro_transitorio(_erro_limite("credit_balance_exhausted"))
    assert not erro_transitorio(_erro_limite("insufficient_quota"))


def test_falha_de_conexao_recebe_tres_tentativas_sem_espera(monkeypatch) -> None:
    """Repete falhas transitórias no máximo três vezes."""
    monkeypatch.setattr(resiliencia_openai, "wait_exponential", lambda **_: lambda _: 0)
    tentativas = 0
    requisicao = httpx.Request("POST", "https://api.openai.com/v1/responses")

    def chamada():
        nonlocal tentativas
        tentativas += 1
        if tentativas < 3:
            raise APIConnectionError(request=requisicao)
        return "ok"

    assert executar_com_retry(chamada) == "ok"
    assert tentativas == 3


def test_saldo_esgotado_falha_na_primeira_tentativa() -> None:
    """Não consome tentativas extras diante de falha permanente."""
    tentativas = 0

    def chamada():
        nonlocal tentativas
        tentativas += 1
        raise _erro_limite("credit_balance_exhausted")

    with pytest.raises(RateLimitError):
        executar_com_retry(chamada)
    assert tentativas == 1
