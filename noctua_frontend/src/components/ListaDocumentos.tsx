import { Documento } from '../tipos'

type PropsListaDocumentos = {
  documentos: Documento[]
  carregando: boolean
}

function rotuloStatus(status: string) {
  return ({ pending: 'Pendente', processing: 'Processando', ready: 'Pronto', failed: 'Falhou' } as Record<string, string>)[status] ?? status
}

export function ListaDocumentos({ documentos, carregando }: PropsListaDocumentos) {
  return (
    <section className="documentos-organizacao">
      <div className="cabecalho-documentos">
        <h2>Documentos da organização</h2>
        <span>{documentos.length} {documentos.length === 1 ? 'arquivo' : 'arquivos'}</span>
      </div>
      {carregando ? (
        <p className="carregando carregamento-documentos">Carregando documentos…</p>
      ) : documentos.length > 0 ? (
        <ul className="grade-documentos">
          {documentos.map(documento => {
            const extensao = documento.nome_arquivo.split('.').pop()?.toLowerCase() ?? 'arq'

            return (
              <li key={documento.id} className="cartao-documento">
                <div className={`icone-arquivo icone-arquivo--${extensao}`}>
                  {extensao.toUpperCase()}
                </div>
                <div className="detalhes-documento">
                  <strong title={documento.nome_arquivo}>{documento.nome_arquivo}</strong>
                  <span className={`status-documento ${documento.status}`}>
                    {rotuloStatus(documento.status)}
                  </span>
                </div>
              </li>
            )
          })}
        </ul>
      ) : (
        <p className="sem-documentos">Nenhum documento enviado ainda.</p>
      )}
    </section>
  )
}
