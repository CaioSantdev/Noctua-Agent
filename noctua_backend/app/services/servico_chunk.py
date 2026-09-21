import tiktoken

from app.core.config import obter_configuracoes


class ServicoChunk:
    """Divide texto em blocos com sobreposição medida em tokens."""

    def dividir(self, texto: str) -> list[str]:
        """Retorna chunks respeitando tamanho e sobreposição configurados."""
        configuracoes = obter_configuracoes()
        codificador = tiktoken.get_encoding("cl100k_base")
        tokens = codificador.encode(texto)
        if not tokens:
            return []
        passo = configuracoes.tamanho_chunk - configuracoes.sobreposicao_chunk
        if passo <= 0:
            raise ValueError("SOBREPOSICAO_CHUNK deve ser menor que TAMANHO_CHUNK.")
        return [
            codificador.decode(tokens[inicio : inicio + configuracoes.tamanho_chunk])
            for inicio in range(0, len(tokens), passo)
        ]
