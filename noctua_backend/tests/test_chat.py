import uuid

import tiktoken

from app.core.config import obter_configuracoes
from app.models.documento import Documento, StatusDocumento
from app.models.trecho_documento import TrechoDocumento
from app.services.servico_chat import RESPOSTA_SEM_CONTEXTO, ServicoChat
from app.services.servico_llm import ServicoLlm
from app.services.servico_rag import ResultadoBusca


def test_chat_nao_usa_llm_quando_nao_encontra_contexto(monkeypatch) -> None:
    """Evita conhecimento geral quando a pergunta não está nos documentos."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    obter_configuracoes.cache_clear()

    class RagFalso:
        def buscar(self, pergunta, organizacao_id):
            assert pergunta == "Quem descobriu o Brasil?"
            assert organizacao_id == organizacao
            return []

    class RepositorioFalso:
        def obter_por_id(self, *args):
            raise AssertionError("Não deve consultar fontes sem chunks recuperados.")

    class LlmFalsa:
        def responder(self, *args):
            raise AssertionError("A LLM não deve ser chamada sem contexto.")

    organizacao = uuid.UUID("00000000-0000-0000-0000-000000000001")
    resposta = ServicoChat(RagFalso(), RepositorioFalso(), LlmFalsa()).responder(
        "Quem descobriu o Brasil?", organizacao
    )

    assert resposta.resposta == RESPOSTA_SEM_CONTEXTO
    assert resposta.fontes == []
    obter_configuracoes.cache_clear()


def test_chat_respeita_orcamento_e_constroi_fontes_dos_chunks(monkeypatch) -> None:
    """Limita o contexto e nunca delega fontes à LLM."""
    organizacao = uuid.UUID("00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("ORGANIZACAO_PADRAO_ID", str(organizacao))
    monkeypatch.setenv("MAX_TOKENS_CONTEXTO", "8")
    obter_configuracoes.cache_clear()

    documento_id = uuid.uuid4()
    trecho = TrechoDocumento(
        documento_id=documento_id,
        organizacao_id=organizacao,
        conteudo="PostgreSQL é o banco de dados utilizado pelo Noctua.",
        pagina=3,
        embedding=[0.1] * 1536,
    )

    class RagFalso:
        def buscar(self, pergunta, organizacao_id):
            assert organizacao_id == organizacao
            return [ResultadoBusca(trecho=trecho, similaridade=0.9)]

    class RepositorioFalso:
        def obter_por_id(self, identificador, organizacao_id):
            assert identificador == documento_id
            assert organizacao_id == organizacao
            return Documento(
                id=documento_id,
                organizacao_id=organizacao,
                nome_arquivo="arquitetura.pdf",
                extensao=".pdf",
                tamanho_bytes=100,
                caminho_arquivo="/tmp/arquitetura.pdf",
                status=StatusDocumento.PRONTO,
            )

    class LlmFalsa:
        def responder(self, pergunta, contexto):
            codificador = tiktoken.get_encoding("cl100k_base")
            assert len(codificador.encode(contexto)) <= 8
            return "O Noctua utiliza PostgreSQL."

    resposta = ServicoChat(RagFalso(), RepositorioFalso(), LlmFalsa()).responder(
        "Qual banco de dados é utilizado?", organizacao
    )

    assert resposta.resposta == "O Noctua utiliza PostgreSQL."
    assert resposta.fontes[0].documento == "arquitetura.pdf"
    assert resposta.fontes[0].pagina == 3
    obter_configuracoes.cache_clear()


def test_servico_llm_usa_responses_sem_armazenar_a_resposta(monkeypatch) -> None:
    """Mantém documentos enviados fora do armazenamento de respostas da API."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("MODELO_LLM", "gpt-4.1-mini")
    obter_configuracoes.cache_clear()

    class RespostaFalsa:
        output_text = "Resposta fundamentada."

    class RespostasFalsas:
        def create(self, **kwargs):
            assert kwargs["model"] == "gpt-4.1-mini"
            assert kwargs["store"] is False
            assert kwargs["max_output_tokens"] == 500
            assert "somente com informações presentes" in kwargs["instructions"]
            return RespostaFalsa()

    class ClienteFalso:
        responses = RespostasFalsas()

    monkeypatch.setattr("app.services.servico_llm.obter_cliente_openai", lambda: ClienteFalso())

    assert ServicoLlm().responder("Qual banco?", "PostgreSQL é utilizado.") == "Resposta fundamentada."
    obter_configuracoes.cache_clear()
