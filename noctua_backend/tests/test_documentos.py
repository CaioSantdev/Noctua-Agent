from collections.abc import Generator
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.documentos import obter_servico_documento
from app.api.dependencies.autenticacao import obter_usuario_autenticado
from app.core.config import obter_configuracoes
from app.infrastructure.banco import obter_sessao
from app.main import app
from app.models.base import Base
from app.models.usuario import Usuario
from app.services.servico_rag import ServicoRag


def test_enviar_listar_e_obter_documento_txt(monkeypatch, tmp_path) -> None:
    """Valida o fluxo síncrono de um documento TXT."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("DIRETORIO_ARQUIVOS", str(tmp_path / "arquivos"))
    obter_configuracoes.cache_clear()
    monkeypatch.setattr(ServicoRag, "indexar_documento", lambda *_: None)

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
            assert documento["status"] == "ready"

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
