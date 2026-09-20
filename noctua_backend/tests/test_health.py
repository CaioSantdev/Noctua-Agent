from fastapi.testclient import TestClient

from app.main import app
from app.services.servico_saude import ServicoSaude


def test_verificar_saude_retorna_ok(monkeypatch) -> None:
    monkeypatch.setattr(ServicoSaude, "banco_disponivel", lambda _: True)

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_verificar_saude_retorna_indisponivel_quando_banco_falha(monkeypatch) -> None:
    monkeypatch.setattr(ServicoSaude, "banco_disponivel", lambda _: False)

    response = TestClient(app).get("/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "O banco de dados não está disponível."}
