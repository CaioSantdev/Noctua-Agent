from app.core.config import obter_configuracoes
from app.infrastructure.cliente_openai import obter_cliente_openai


class ServicoEmbedding:
    """Gera embeddings com o modelo configurado da OpenAI."""

    def gerar(self, texto: str) -> list[float]:
        """Gera um embedding para texto não vazio."""
        if not texto.strip():
            raise ValueError("Não é possível gerar embedding de texto vazio.")
        resposta = obter_cliente_openai().embeddings.create(
            model=obter_configuracoes().modelo_embedding, input=texto
        )
        return resposta.data[0].embedding
