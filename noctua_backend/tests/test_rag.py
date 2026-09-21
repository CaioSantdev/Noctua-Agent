import uuid

import tiktoken
from app.core.config import obter_configuracoes
from app.models.trecho_documento import TrechoDocumento
from app.services.servico_chunk import ServicoChunk
from app.services.servico_embedding import ServicoEmbedding
from app.services.servico_rag import ServicoRag


def test_dividir_aplica_sobreposicao_em_tokens(monkeypatch) -> None:
    """Mantém tokens compartilhados entre chunks consecutivos."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("TAMANHO_CHUNK", "4")
    monkeypatch.setenv("SOBREPOSICAO_CHUNK", "1")
    obter_configuracoes.cache_clear()

    chunks = ServicoChunk().dividir("um dois tres quatro cinco seis sete oito")

    assert len(chunks) >= 2
    codificador = tiktoken.get_encoding("cl100k_base")
    assert codificador.encode(chunks[0])[-1:] == codificador.encode(chunks[1])[:1]
    obter_configuracoes.cache_clear()


def test_busca_restringe_resultados_a_organizacao_do_backend(monkeypatch) -> None:
    """Não permite que a busca escolha organização por entrada do cliente."""
    organizacao = uuid.UUID("00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("ORGANIZACAO_PADRAO_ID", str(organizacao))
    monkeypatch.setenv("LIMIAR_SIMILARIDADE", "0.70")
    obter_configuracoes.cache_clear()
    monkeypatch.setattr(ServicoEmbedding, "gerar", lambda *_: [0.1] * 1536)

    trecho = TrechoDocumento(
        documento_id=uuid.uuid4(),
        organizacao_id=organizacao,
        conteudo="O sistema utiliza PostgreSQL como banco de dados.",
        pagina=1,
        embedding=[0.1] * 1536,
    )

    class RepositorioFalso:
        def buscar_semelhantes(self, organizacao_id, embedding, limite):
            assert organizacao_id == organizacao
            assert len(embedding) == 1536
            assert limite == 5
            return [(trecho, 0.08)]

    resultados = ServicoRag(RepositorioFalso()).buscar(
        "Qual banco a aplicação utiliza?", organizacao
    )

    assert len(resultados) == 1
    assert resultados[0].trecho.conteudo == "O sistema utiliza PostgreSQL como banco de dados."
    assert resultados[0].similaridade == 0.92
    obter_configuracoes.cache_clear()


def test_busca_recebe_pergunta_em_alemao_sem_escolher_organizacao(monkeypatch) -> None:
    """Aceita consultas multilíngues e preserva o isolamento no backend."""
    organizacao = uuid.UUID("00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("ORGANIZACAO_PADRAO_ID", str(organizacao))
    monkeypatch.setenv("LIMIAR_SIMILARIDADE", "0.30")
    obter_configuracoes.cache_clear()

    pergunta = "Was ist das Ziel der technischen Herausforderung?"
    monkeypatch.setattr(ServicoEmbedding, "gerar", lambda _, texto: [0.1] * 1536)
    trecho = TrechoDocumento(
        documento_id=uuid.uuid4(),
        organizacao_id=organizacao,
        conteudo="Criar um protótipo de agente de conhecimento.",
        pagina=1,
        embedding=[0.1] * 1536,
    )

    class RepositorioFalso:
        def buscar_semelhantes(self, organizacao_id, embedding, limite):
            assert organizacao_id == organizacao
            return [(trecho, 0.65)]

    resultados = ServicoRag(RepositorioFalso()).buscar(pergunta, organizacao)

    assert len(resultados) == 1
    assert resultados[0].similaridade == 0.35
    obter_configuracoes.cache_clear()
