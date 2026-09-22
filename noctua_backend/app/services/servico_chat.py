import uuid
from dataclasses import dataclass

import tiktoken

from app.core.config import obter_configuracoes
from app.repositories.repositorio_documento import RepositorioDocumento
from app.services.servico_llm import ServicoLlm
from app.services.servico_rag import ResultadoBusca, ServicoRag

RESPOSTA_SEM_CONTEXTO = (
    "Não encontrei informações suficientes nos documentos disponíveis para responder essa pergunta."
)
LIMITE_CARACTERES_PREVIA_FONTE = 220


@dataclass(frozen=True)
class FonteResposta:
    """Fonte recuperada e incluída no contexto enviado à LLM."""

    documento: str
    pagina: int | None
    trecho: str


@dataclass(frozen=True)
class RespostaChat:
    """Resposta do agente e as fontes que a fundamentam."""

    resposta: str
    fontes: list[FonteResposta]


class ServicoChat:
    """Orquestra recuperação, contexto, LLM e fontes da conversa."""

    def __init__(
        self,
        servico_rag: ServicoRag,
        repositorio_documento: RepositorioDocumento,
        servico_llm: ServicoLlm | None = None,
    ) -> None:
        self.servico_rag = servico_rag
        self.repositorio_documento = repositorio_documento
        self.servico_llm = servico_llm or ServicoLlm()

    def responder(self, pergunta: str, organizacao_id: uuid.UUID) -> RespostaChat:
        """Responde uma pergunta apenas quando há contexto recuperado."""
        resultados = self.servico_rag.buscar(pergunta, organizacao_id)
        fontes = self._obter_fontes(resultados, organizacao_id)
        contexto = self._montar_contexto(resultados)
        if not contexto:
            return RespostaChat(resposta=RESPOSTA_SEM_CONTEXTO, fontes=[])

        return RespostaChat(
            resposta=self.servico_llm.responder(pergunta, contexto),
            fontes=fontes,
        )

    def _montar_contexto(self, resultados: list[ResultadoBusca]) -> str:
        """Combina trechos recuperados sem ultrapassar o orçamento de tokens."""
        limite = obter_configuracoes().max_tokens_contexto
        codificador = tiktoken.get_encoding("cl100k_base")
        tokens_contexto: list[int] = []

        for resultado in resultados:
            tokens_trecho = codificador.encode(resultado.trecho.conteudo)
            espaco_disponivel = limite - len(tokens_contexto)
            if espaco_disponivel <= 0:
                break
            tokens_contexto.extend(tokens_trecho[:espaco_disponivel])

        return codificador.decode(tokens_contexto)

    def _obter_fontes(
        self, resultados: list[ResultadoBusca], organizacao_id: uuid.UUID
    ) -> list[FonteResposta]:
        """Cria fontes a partir dos chunks, sem pedir metadados à LLM."""
        fontes: list[FonteResposta] = []
        fontes_vistas: set[tuple[str, int | None, str]] = set()

        for resultado in resultados:
            documento = self.repositorio_documento.obter_por_id(
                resultado.trecho.documento_id, organizacao_id
            )
            if documento is None:
                continue
            trecho = self._criar_previa(resultado.trecho.conteudo)
            chave = (documento.nome_arquivo, resultado.trecho.pagina, trecho)
            if chave not in fontes_vistas:
                fontes.append(
                    FonteResposta(
                        documento=documento.nome_arquivo,
                        pagina=resultado.trecho.pagina,
                        trecho=trecho,
                    )
                )
                fontes_vistas.add(chave)
        return fontes

    @staticmethod
    def _criar_previa(conteudo: str) -> str:
        """Limita a citação para manter a resposta legível e econômica."""
        texto_normalizado = " ".join(conteudo.split())
        if len(texto_normalizado) <= LIMITE_CARACTERES_PREVIA_FONTE:
            return texto_normalizado
        return f"{texto_normalizado[:LIMITE_CARACTERES_PREVIA_FONTE - 1].rstrip()}…"
