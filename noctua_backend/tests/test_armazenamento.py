from app.infrastructure import armazenamento


class RespostaFalsa:
    """Simula a resposta HTTP do Supabase Storage sem acessar a rede."""

    def __init__(self, conteudo: bytes) -> None:
        self.conteudo = conteudo

    def __enter__(self) -> "RespostaFalsa":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return self.conteudo


def test_armazenamento_supabase_envia_e_le_documento(monkeypatch) -> None:
    """Usa a chave de serviço apenas no backend para persistir um objeto privado."""
    requisicoes: list[object] = []

    def urlopen_falso(requisicao, timeout):
        assert timeout == 30
        requisicoes.append(requisicao)
        return RespostaFalsa(b"conteudo recuperado")

    monkeypatch.setattr(armazenamento, "urlopen", urlopen_falso)
    servico = armazenamento.ArmazenamentoSupabase(
        "https://exemplo.supabase.co", "segredo-de-teste", "documentos"
    )

    chave = servico.salvar("organizacao/arquivo.txt", b"conteudo enviado")
    conteudo = servico.ler(chave)

    assert chave == "organizacao/arquivo.txt"
    assert conteudo == b"conteudo recuperado"
    envio, leitura = requisicoes
    assert envio.method == "POST"
    assert envio.data == b"conteudo enviado"
    assert envio.get_header("X-upsert") == "true"
    assert leitura.method == "GET"
    assert "organizacao/arquivo.txt" in leitura.full_url
