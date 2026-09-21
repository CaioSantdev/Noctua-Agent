import { ChangeEvent } from 'react'

type PropsPainelEnvio = {
  arquivo: File | null
  carregando: boolean
  aoSelecionarArquivo: (evento: ChangeEvent<HTMLInputElement>) => void
  aoEnviar: () => void
}

export function PainelEnvio({ arquivo, carregando, aoSelecionarArquivo, aoEnviar }: PropsPainelEnvio) {
  return (
    <section className="painel-central">
      <div>
        <h2>Envie um documento</h2>
        <p>Formatos aceitos: PDF ou TXT</p>
      </div>
      <div className="linha-acao">
        <label className="seletor-arquivo" htmlFor="arquivo">
          {arquivo?.name ?? 'Escolher arquivo'}
        </label>
        <input id="arquivo" type="file" accept=".pdf,.txt" onChange={aoSelecionarArquivo} />
        <button className="botao-seta" aria-label="Enviar arquivo" disabled={!arquivo || carregando} onClick={aoEnviar}>
          →
        </button>
      </div>
    </section>
  )
}
