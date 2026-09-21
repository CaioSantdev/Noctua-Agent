import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.documento import Documento, StatusDocumento
from app.models.organizacao import Organizacao
from app.models.usuario import Usuario
from app.repositories.repositorio_documento import RepositorioDocumento


def test_tenant_a_nao_lista_nem_acessa_documento_do_tenant_b() -> None:
    """Impede que um identificador conhecido contorne o isolamento de tenant."""
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
    sessao.close()
