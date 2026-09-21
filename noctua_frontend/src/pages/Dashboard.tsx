import { ChangeEvent, KeyboardEvent } from 'react'

import { Aviso } from '../components/Aviso'
import { ListaDocumentos } from '../components/ListaDocumentos'
import { PainelChat } from '../components/PainelChat'
import { PainelEnvio } from '../components/PainelEnvio'
import { Documento, Estado, Fonte, ModoDashboard } from '../tipos'

type PropsDashboard = {
  modo: ModoDashboard
  arquivo: File | null
  pergunta: string
  resposta: string
  fontes: Fonte[]
  documentos: Documento[]
  estado: Estado
  mensagem: string
  carregandoDocumentos: boolean
  aoSair: () => void
  aoSelecionarEnvio: () => void
  aoSelecionarChat: () => void
  aoSelecionarArquivo: (evento: ChangeEvent<HTMLInputElement>) => void
  aoEnviarArquivo: () => void
  aoAlterarPergunta: (evento: ChangeEvent<HTMLInputElement>) => void
  aoPressionarTecla: (evento: KeyboardEvent<HTMLInputElement>) => void
  aoPerguntar: () => void
}

export function Dashboard({
  modo,
  arquivo,
  pergunta,
  resposta,
  fontes,
  documentos,
  estado,
  mensagem,
  carregandoDocumentos,
  aoSair,
  aoSelecionarEnvio,
  aoSelecionarChat,
  aoSelecionarArquivo,
  aoEnviarArquivo,
  aoAlterarPergunta,
  aoPressionarTecla,
  aoPerguntar,
}: PropsDashboard) {
  const imagemModo = modo === 'enviar'
    ? { caminho: '/imagens/coruja_livro_insere.jpg', descricao: 'Coruja Noctua organizando livros' }
    : { caminho: '/imagens/coruja_lupa_busca.jpg', descricao: 'Coruja Noctua pesquisando documentos' }

  return (
    <main className="dashboard">
      <header className="cabecalho-principal">
        <div className="marca-dashboard">
          <img src="/imagens/logo_noctua.png" alt="" />
          <span>NOCTUA</span>
        </div>
        <button className="sair" onClick={aoSair}>Sair</button>
      </header>

      <section className="conteudo-dashboard">
        <div className="titulo-dashboard">
          <p className="etiqueta">BASE DE CONHECIMENTO</p>
          <h1>Seu conhecimento, organizado.</h1>
        </div>

        <div className="area-central">
          <img
            className="ilustracao-dashboard"
            src={imagemModo.caminho}
            alt={imagemModo.descricao}
          />
          <nav className="seletor-modo" aria-label="Ação do dashboard">
            <button className={modo === 'enviar' ? 'ativo' : ''} onClick={aoSelecionarEnvio}>
              Enviar documento
            </button>
            <button className={modo === 'perguntar' ? 'ativo' : ''} onClick={aoSelecionarChat}>
              Chat
            </button>
          </nav>

          {modo === 'enviar' ? (
            <PainelEnvio
              arquivo={arquivo}
              carregando={estado === 'carregando'}
              aoSelecionarArquivo={aoSelecionarArquivo}
              aoEnviar={aoEnviarArquivo}
            />
          ) : (
            <PainelChat
              pergunta={pergunta}
              carregando={estado === 'carregando'}
              aoAlterarPergunta={aoAlterarPergunta}
              aoPressionarTecla={aoPressionarTecla}
              aoPerguntar={aoPerguntar}
            />
          )}

          <Aviso estado={estado} mensagem={mensagem} />
          {resposta && (
            <article className="resposta">
              <p>{resposta}</p>
              {fontes.length > 0 && (
                <div>
                  <strong>Fontes</strong>
                  <ul>
                    {fontes.map((fonte, indice) => (
                      <li key={`${fonte.document}-${fonte.page}-${indice}`}>
                        {fonte.document}{fonte.page ? ` · página ${fonte.page}` : ''}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </article>
          )}
        </div>

        <ListaDocumentos documentos={documentos} carregando={carregandoDocumentos} />
      </section>
    </main>
  )
}
