import uuid
from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader

from app.core.config import obter_configuracoes
from app.models.documento import Documento
from app.models.trecho_documento import TrechoDocumento
from app.repositories.repositorio_trecho import RepositorioTrecho
from app.services.servico_chunk import ServicoChunk
from app.services.servico_embedding import ServicoEmbedding


@dataclass(frozen=True)
class ResultadoBusca:
    """Trecho recuperado e sua similaridade semântica."""

    trecho: TrechoDocumento
    similaridade: float


class ServicoRag:
    """Indexa documentos e recupera trechos vetoriais por organização."""

    def __init__(self, repositorio: RepositorioTrecho) -> None:
        self.repositorio = repositorio
        self.servico_chunk = ServicoChunk()
        self.servico_embedding = ServicoEmbedding()

    def indexar_documento(self, documento: Documento, conteudo_arquivo: bytes | None = None) -> None:
        """Gera chunks e embeddings para um documento com texto extraído."""
        if not documento.texto_extraido:
            return

        self.repositorio.remover_por_documento(documento.id)
        trechos = [
            TrechoDocumento(
                documento_id=documento.id,
                organizacao_id=documento.organizacao_id,
                conteudo=conteudo,
                pagina=pagina,
                embedding=self.servico_embedding.gerar(conteudo),
            )
            for pagina, texto in self._obter_paginas(documento, conteudo_arquivo)
            for conteudo in self.servico_chunk.dividir(texto)
        ]
        if trechos:
            self.repositorio.adicionar_varios(trechos)

    def buscar(self, pergunta: str, organizacao_id: uuid.UUID) -> list[ResultadoBusca]:
        """Busca trechos similares na organização configurada no servidor."""
        configuracoes = obter_configuracoes()
        resultados = self.repositorio.buscar_semelhantes(
            organizacao_id=organizacao_id,
            embedding=self.servico_embedding.gerar(pergunta),
            limite=configuracoes.max_trechos_recuperados,
        )
        return [
            ResultadoBusca(trecho=trecho, similaridade=1 - distancia)
            for trecho, distancia in resultados
            if 1 - distancia >= configuracoes.limiar_similaridade
        ]

    def _obter_paginas(
        self, documento: Documento, conteudo_arquivo: bytes | None
    ) -> list[tuple[int | None, str]]:
        """Recupera texto por página para preservar a fonte dos chunks."""
        if documento.extensao == ".txt":
            return [(None, documento.texto_extraido or "")]

        if conteudo_arquivo is None:
            raise ValueError("O conteúdo do PDF é necessário para indexação.")

        leitor = PdfReader(BytesIO(conteudo_arquivo))
        return [
            (numero, pagina.extract_text() or "")
            for numero, pagina in enumerate(leitor.pages, start=1)
        ]
