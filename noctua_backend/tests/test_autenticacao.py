import uuid

from app.core.config import obter_configuracoes
from app.core.seguranca import (
    criar_token_acesso,
    gerar_hash_senha,
    obter_usuario_id_do_token,
    verificar_senha,
)
from app.models.usuario import Usuario


def test_senha_e_armazenada_com_hash_scrypt() -> None:
    """Nunca mantém a senha original no valor persistível."""
    senha_hash = gerar_hash_senha("senha-segura")

    assert senha_hash.startswith("scrypt$")
    assert "senha-segura" not in senha_hash
    assert verificar_senha("senha-segura", senha_hash)
    assert not verificar_senha("senha-incorreta", senha_hash)


def test_token_identifica_apenas_usuario_autenticado(monkeypatch) -> None:
    """Assina e valida a identidade que determina o tenant no servidor."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite://")
    monkeypatch.setenv("JWT_SECRET", "segredo-de-teste-com-mais-de-trinta-e-dois-caracteres")
    obter_configuracoes.cache_clear()
    usuario = Usuario(id=uuid.uuid4(), organizacao_id=uuid.uuid4(), email="a@noctua.local", senha_hash="hash")

    token = criar_token_acesso(usuario)

    assert obter_usuario_id_do_token(token) == usuario.id
    obter_configuracoes.cache_clear()
