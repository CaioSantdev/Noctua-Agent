from collections.abc import Generator
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.documentos import obter_servico_documento
from app.api.dependencies.autenticacao import obter_usuario_autenticado
from app.core.config import obter_configuracoes
from app.infrastructure import tarefas_documento
from app.infrastructure.banco import obter_sessao
from app.main import app
from app.models.base import Base
from app.models.documento import StatusDocumento
from app.models.usuario import Usuario
from app.repositories.repositorio_documento import RepositorioDocumento
from app.services import servico_documento
from app.services.servico_documento import ServicoDocumento
from app.services.servico_rag import ServicoRag


def test_enviar_listar_e_obter_documento_txt(monkeypatch, tmp_path) -> None:
    """Valida que o envio registra um TXT pendente para o worker."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("DIRETORIO_ARQUIVOS", str(tmp_path / "arquivos"))
    obter_configuracoes.cache_clear()
    tarefas_enfileiradas: list[uuid.UUID] = []
    monkeypatch.setattr(
        servico_documento,
        "enfileirar_processamento_documento",
        lambda identificador: tarefas_enfileiradas.append(identificador),
    )

    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    fabrica_sessoes = sessionmaker(bind=engine, expire_on_commit=False)

    def fornecer_sessao() -> Generator[Session, None, None]:
        with fabrica_sessoes() as sessao:
            yield sessao

    usuario = Usuario(
        id=uuid.uuid4(), organizacao_id=uuid.uuid4(), email="teste@noctua.local", senha_hash="hash"
    )
    app.dependency_overrides[obter_sessao] = fornecer_sessao
    app.dependency_overrides[obter_usuario_autenticado] = lambda: usuario
    try:
        with TestClient(app) as cliente:
            resposta_envio = cliente.post(
                "/documents",
                files={"arquivo": ("anotacoes.txt", b"O Noctua armazena documentos.", "text/plain")},
            )

            assert resposta_envio.status_code == 201
            documento = resposta_envio.json()
            assert documento["nome_arquivo"] == "anotacoes.txt"
            assert documento["status"] == StatusDocumento.PENDENTE
            assert tarefas_enfileiradas == [uuid.UUID(documento["id"])]

            resposta_lista = cliente.get("/documents")
            assert resposta_lista.status_code == 200
            assert len(resposta_lista.json()) == 1

            resposta_detalhe = cliente.get(f"/documents/{documento['id']}")
            assert resposta_detalhe.status_code == 200
            assert resposta_detalhe.json()["tamanho_bytes"] == len(b"O Noctua armazena documentos.")
    finally:
        app.dependency_overrides.clear()
        obter_configuracoes.cache_clear()


def test_rejeita_extensao_nao_permitida(monkeypatch, tmp_path) -> None:
    """Impede o envio de arquivos fora dos formatos suportados."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("DIRETORIO_ARQUIVOS", str(tmp_path / "arquivos"))
    obter_configuracoes.cache_clear()

    with TestClient(app) as cliente:
        resposta = cliente.post("/documents", files={"arquivo": ("imagem.png", b"conteudo", "image/png")})

    assert resposta.status_code == 401
    obter_configuracoes.cache_clear()


def test_worker_processa_documento_pendente_ate_pronto(monkeypatch, tmp_path) -> None:
    """Valida a transição PENDING → PROCESSING → READY no worker."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("DIRETORIO_ARQUIVOS", str(tmp_path / "arquivos"))
    obter_configuracoes.cache_clear()
    monkeypatch.setattr(servico_documento, "enfileirar_processamento_documento", lambda _: None)
    estados_durante_indexacao: list[StatusDocumento] = []
    monkeypatch.setattr(
        ServicoRag,
        "indexar_documento",
        lambda _, documento: estados_durante_indexacao.append(documento.status),
    )

    engine = create_engine("sqlite+pysqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    fabrica_sessoes = sessionmaker(bind=engine, expire_on_commit=False)
    organizacao_id = uuid.uuid4()

    with fabrica_sessoes() as sessao:
        repositorio = RepositorioDocumento(sessao)
        documento = ServicoDocumento(repositorio, organizacao_id).criar(
            "manual.txt", b"Conteudo para processamento assincrono."
        )
        assert documento.status == StatusDocumento.PENDENTE

    monkeypatch.setattr(tarefas_documento, "obter_fabrica_sessoes", lambda: fabrica_sessoes)
    tarefas_documento.processar_documento.run(str(documento.id))

    with fabrica_sessoes() as sessao:
        documento_processado = RepositorioDocumento(sessao).obter_por_id_interno(documento.id)
        assert documento_processado is not None
        assert documento_processado.status == StatusDocumento.PRONTO
        assert documento_processado.texto_extraido == "Conteudo para processamento assincrono."
    assert estados_durante_indexacao == [StatusDocumento.PROCESSANDO]
    obter_configuracoes.cache_clear()


def test_worker_marca_documento_como_falhou_quando_indexacao_falha(monkeypatch, tmp_path) -> None:
    """Garante que falhas do worker fiquem visíveis como FAILED."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("DIRETORIO_ARQUIVOS", str(tmp_path / "arquivos"))
    obter_configuracoes.cache_clear()
    monkeypatch.setattr(servico_documento, "enfileirar_processamento_documento", lambda _: None)

    def falhar_indexacao(*_: object) -> None:
        raise RuntimeError("Falha simulada da indexação.")

    monkeypatch.setattr(ServicoRag, "indexar_documento", falhar_indexacao)
    engine = create_engine("sqlite+pysqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    fabrica_sessoes = sessionmaker(bind=engine, expire_on_commit=False)
    organizacao_id = uuid.uuid4()

    with fabrica_sessoes() as sessao:
        repositorio = RepositorioDocumento(sessao)
        documento = ServicoDocumento(repositorio, organizacao_id).criar(
            "falha.txt", "Conteúdo que deve falhar na indexação.".encode("utf-8")
        )

    monkeypatch.setattr(tarefas_documento, "obter_fabrica_sessoes", lambda: fabrica_sessoes)
    tarefas_documento.processar_documento.run(str(documento.id))

    with fabrica_sessoes() as sessao:
        documento_processado = RepositorioDocumento(sessao).obter_por_id_interno(documento.id)
        assert documento_processado is not None
        assert documento_processado.status == StatusDocumento.FALHOU
    obter_configuracoes.cache_clear()
