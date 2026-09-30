import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import obter_configuracoes
from app.models.base import Base
from app.models.documento import Documento, StatusDocumento
from app.models.organizacao import Organizacao
from app.models.usuario import Usuario
from app.repositories.repositorio_documento import RepositorioDocumento
from app.services.servico_documento import ServicoDocumento


def test_tenant_a_nao_lista_nem_acessa_documento_do_tenant_b(monkeypatch, tmp_path) -> None:
    """Impede que um identificador conhecido contorne o isolamento de tenant."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("DIRETORIO_ARQUIVOS", str(tmp_path / "arquivos"))
    obter_configuracoes.cache_clear()
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    sessao = sessionmaker(bind=engine, expire_on_commit=False)()
    organizacao_a = Organizacao(id=uuid.uuid4(), nome="Organização A")
    organizacao_b = Organizacao(id=uuid.uuid4(), nome="Organização B")
    sessao.add_all([organizacao_a, organizacao_b])
    documento_a = Documento(
        organizacao_id=organizacao_a.id,
        nome_arquivo="documento-a.txt",
        extensao=".txt",
        tamanho_bytes=1,
        caminho_arquivo="/tmp/a.txt",
        status=StatusDocumento.PRONTO,
    )
    documento_b = Documento(
        organizacao_id=organizacao_b.id,
        nome_arquivo="documento-b.txt",
        extensao=".txt",
        tamanho_bytes=1,
        caminho_arquivo="/tmp/b.txt",
        status=StatusDocumento.PRONTO,
    )
    sessao.add_all([documento_a, documento_b])
    sessao.commit()
    repositorio = RepositorioDocumento(sessao)

    documentos_a = repositorio.listar(organizacao_a.id)

    assert [documento.id for documento in documentos_a] == [documento_a.id]
    assert repositorio.obter_por_id(documento_b.id, organizacao_a.id) is None
    servico_a = ServicoDocumento(repositorio, organizacao_a.id)
    assert not servico_a.remover(documento_b.id)
    assert repositorio.obter_por_id_interno(documento_b.id) is not None

    obter_configuracoes.cache_clear()
    sessao.close()
