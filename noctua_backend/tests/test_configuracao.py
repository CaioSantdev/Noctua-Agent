from app.core.config import obter_configuracoes, obter_origens_cors


def test_normaliza_url_postgresql_para_driver_psycopg(monkeypatch) -> None:
    """Aceita a URL PostgreSQL fornecida por provedores externos."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://usuario:senha@host:5432/noctua")
    monkeypatch.setenv("ORIGENS_CORS", "https://noctua.vercel.app, http://localhost:5173")
    obter_configuracoes.cache_clear()

    configuracoes = obter_configuracoes()

    assert configuracoes.url_banco.startswith("postgresql+psycopg://")
    assert obter_origens_cors() == (
        "https://noctua.vercel.app",
        "http://localhost:5173",
    )
    obter_configuracoes.cache_clear()
