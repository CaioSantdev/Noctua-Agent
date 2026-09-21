import { ChangeEvent, KeyboardEvent } from 'react'

type PropsPainelChat = {
  pergunta: string
  carregando: boolean
  aoAlterarPergunta: (evento: ChangeEvent<HTMLInputElement>) => void
  aoPressionarTecla: (evento: KeyboardEvent<HTMLInputElement>) => void
  aoPerguntar: () => void
}

export function PainelChat({ pergunta, carregando, aoAlterarPergunta, aoPressionarTecla, aoPerguntar }: PropsPainelChat) {
  return (
    <section className="painel-central">
      <h2>Faça uma pergunta</h2>
      <div className="linha-acao">
        <input
          value={pergunta}
          onChange={aoAlterarPergunta}
          onKeyDown={aoPressionarTecla}
          placeholder="Pergunte algo sobre seus documentos"
        />
        <button className="botao-seta" aria-label="Enviar pergunta" onClick={aoPerguntar} disabled={carregando || !pergunta.trim()}>
          →
        </button>
      </div>
    </section>
  )
}
