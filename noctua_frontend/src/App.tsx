import { FormEvent, useEffect, useState } from 'react'

const api = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
type Documento = { id: string; nome_arquivo: string; status: string }
type Fonte = { document: string; page: number | null }
type Estado = 'neutro' | 'carregando' | 'sucesso' | 'erro'
type Rota = '/login' | '/cadastro' | '/dashboard'

function mensagemErro(valor: unknown, fallback: string) {
  return valor instanceof Error ? valor.message : fallback
}

function rotuloStatus(status: string) {
  return ({ pending: 'Pendente', processing: 'Processando', ready: 'Pronto', failed: 'Falhou' } as Record<string, string>)[status] ?? status
}

function obterRota(caminho: string): Rota {
  return caminho === '/cadastro' || caminho === '/dashboard' ? caminho : '/login'
}

export default function App() {
  const [autenticado, setAutenticado] = useState(Boolean(sessionStorage.getItem('noctua_token')))
  const [rota, setRota] = useState<Rota>(() => obterRota(window.location.pathname))
  const [modo, setModo] = useState<'enviar' | 'perguntar'>('enviar')
  const [senhaVisivel, setSenhaVisivel] = useState(false)
  const [documentos, setDocumentos] = useState<Documento[]>([])
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [pergunta, setPergunta] = useState('')
  const [resposta, setResposta] = useState('')
  const [fontes, setFontes] = useState<Fonte[]>([])
  const [estado, setEstado] = useState<Estado>('neutro')
  const [mensagem, setMensagem] = useState('')
  const [carregandoDocumentos, setCarregandoDocumentos] = useState(false)

  const cadastro = rota === '/cadastro'

  function navegar(proximaRota: Rota, substituir = false) {
    window.history[substituir ? 'replaceState' : 'pushState']({}, '', proximaRota)
    setRota(proximaRota)
  }

  function encerrarSessao() {
    sessionStorage.removeItem('noctua_token')
    setAutenticado(false)
    navegar('/login', true)
  }

  function selecionarEnvio() {
    setModo('enviar')
    setEstado('neutro')
    setResposta('')
    setFontes([])
  }

  function selecionarChat() {
    setModo('perguntar')
    setEstado('neutro')
  }

  function cabecalhos() {
    return { Authorization: `Bearer ${sessionStorage.getItem('noctua_token')}` }
  }

  async function lerResposta(respostaHttp: Response) {
    const corpo = await respostaHttp.json().catch(() => ({})) as { detail?: string }
    if (respostaHttp.status === 401) encerrarSessao()
    if (!respostaHttp.ok) throw new Error(corpo.detail || 'Não foi possível concluir a solicitação.')
    return corpo
  }

  async function carregarDocumentos() {
    setCarregandoDocumentos(true)
    try {
      const corpo = await lerResposta(await fetch(`${api}/documents`, { headers: cabecalhos() }))
      setDocumentos(corpo as Documento[])
    } catch (erro) {
      setEstado('erro')
      setMensagem(mensagemErro(erro, 'Não foi possível carregar os documentos.'))
    } finally {
      setCarregandoDocumentos(false)
    }
  }

  useEffect(() => {
    const atualizarRota = () => setRota(obterRota(window.location.pathname))
    window.addEventListener('popstate', atualizarRota)
    return () => window.removeEventListener('popstate', atualizarRota)
  }, [])

  useEffect(() => {
    if (autenticado && rota !== '/dashboard') navegar('/dashboard', true)
    if (!autenticado && rota === '/dashboard') navegar('/login', true)
  }, [autenticado, rota])

  useEffect(() => { if (autenticado) void carregarDocumentos() }, [autenticado])

  async function entrar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setEstado('carregando')
    setMensagem(cadastro ? 'Criando sua conta…' : 'Entrando…')
    const formulario = new FormData(evento.currentTarget)
    const corpo = cadastro
      ? { nome_organizacao: formulario.get('organizacao'), email: formulario.get('email'), senha: formulario.get('senha') }
      : { email: formulario.get('email'), senha: formulario.get('senha') }
    try {
      const respostaHttp = await fetch(`${api}${cadastro ? '/auth/register' : '/auth/login'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(corpo),
      })
      const respostaApi = await lerResposta(respostaHttp) as { access_token: string }
      sessionStorage.setItem('noctua_token', respostaApi.access_token)
      setMensagem('Acesso realizado com sucesso.')
      setEstado('sucesso')
      setAutenticado(true)
    } catch (erro) {
      setEstado('erro')
      setMensagem(mensagemErro(erro, 'Não foi possível conectar à API.'))
    }
  }

  async function enviarArquivo() {
    if (!arquivo) return
    setEstado('carregando')
    setMensagem(`Enviando ${arquivo.name}…`)
    const formulario = new FormData()
    formulario.append('arquivo', arquivo)
    try {
      await lerResposta(await fetch(`${api}/documents`, {
        method: 'POST',
        headers: cabecalhos(),
        body: formulario,
      }))
      setArquivo(null)
      setEstado('sucesso')
      setMensagem('Documento enviado e indexado com sucesso.')
      await carregarDocumentos()
    } catch (erro) {
      setEstado('erro')
      setMensagem(mensagemErro(erro, 'Falha no envio do documento.'))
    }
  }

  async function perguntar() {
    if (!pergunta.trim()) return
    setEstado('carregando')
    setMensagem('Consultando sua base de conhecimento…')
    setResposta('')
    setFontes([])
    try {
      const respostaHttp = await fetch(`${api}/chat`, {
        method: 'POST',
        headers: { ...cabecalhos(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: pergunta.trim() }),
      })
      const respostaApi = await lerResposta(respostaHttp) as { answer: string; sources: Fonte[] }
      setResposta(respostaApi.answer)
      setFontes(respostaApi.sources)
      setEstado('sucesso')
      setMensagem('Resposta encontrada.')
    } catch (erro) {
      setEstado('erro')
      setMensagem(mensagemErro(erro, 'Falha ao consultar a base.'))
    }
  }

  const aviso = estado !== 'neutro' && <p className={`aviso ${estado}`} role={estado === 'erro' ? 'alert' : 'status'}>{mensagem}</p>
  const imagemModo = modo === 'enviar'
    ? { caminho: '/imagens/coruja_livro_insere.jpg', descricao: 'Coruja Noctua organizando livros' }
    : { caminho: '/imagens/coruja_lupa_busca.jpg', descricao: 'Coruja Noctua pesquisando documentos' }

  if (autenticado) {
    return (
      <main className="dashboard">
        <header className="cabecalho-principal">
          <div className="marca-dashboard">
            <img src="/imagens/favicon.ico" alt="" />
            <span>NOCTUA</span>
          </div>
          <button className="sair" onClick={encerrarSessao}>Sair</button>
        </header>

        <section className="conteudo-dashboard">
          <div className="titulo-dashboard">
            <p className="etiqueta">BASE DE CONHECIMENTO</p>
            <h1>Seu conhecimento, organizado.</h1>
          </div>

          <div className="area-central">
            <img className="ilustracao-dashboard" src={imagemModo.caminho} alt={imagemModo.descricao} />
            <nav className="seletor-modo" aria-label="Ação do dashboard">
              <button className={modo === 'enviar' ? 'ativo' : ''} onClick={selecionarEnvio}>
                Enviar documento
              </button>
              <button className={modo === 'perguntar' ? 'ativo' : ''} onClick={selecionarChat}>
                Chat
              </button>
            </nav>

            <section className="painel-central">
              {modo === 'enviar' ? (
                <>
                  <div>
                    <h2>Envie um documento</h2>
                    <p>Formatos aceitos: PDF ou TXT</p>
                  </div>
                  <div className="linha-acao">
                    <label className="seletor-arquivo" htmlFor="arquivo">
                      {arquivo?.name ?? 'Escolher arquivo'}
                    </label>
                    <input
                      id="arquivo"
                      type="file"
                      accept=".pdf,.txt"
                      onChange={evento => setArquivo(evento.target.files?.[0] ?? null)}
                    />
                    <button
                      className="botao-seta"
                      aria-label="Enviar arquivo"
                      disabled={!arquivo || estado === 'carregando'}
                      onClick={enviarArquivo}
                    >
                      →
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <h2>Faça uma pergunta</h2>
                  <div className="linha-acao">
                    <input
                      value={pergunta}
                      onChange={evento => setPergunta(evento.target.value)}
                      onKeyDown={evento => {
                        if (evento.key === 'Enter') void perguntar()
                      }}
                      placeholder="Pergunte algo sobre seus documentos"
                    />
                    <button
                      className="botao-seta"
                      aria-label="Enviar pergunta"
                      onClick={perguntar}
                      disabled={estado === 'carregando' || !pergunta.trim()}
                    >
                      →
                    </button>
                  </div>
                </>
              )}
            </section>

            {aviso}
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

          <section className="documentos-organizacao">
            <div className="cabecalho-documentos">
              <h2>Documentos da organização</h2>
              <span>{documentos.length} {documentos.length === 1 ? 'arquivo' : 'arquivos'}</span>
            </div>
            {carregandoDocumentos ? (
              <p className="carregando carregamento-documentos">Carregando documentos…</p>
            ) : documentos.length > 0 ? (
              <ul className="grade-documentos">
                {documentos.map(documento => (
                  <li key={documento.id} className="cartao-documento">
                    <div className="icone-arquivo">
                      {documento.nome_arquivo.split('.').pop()?.toUpperCase() ?? 'ARQ'}
                    </div>
                    <div>
                      <strong title={documento.nome_arquivo}>{documento.nome_arquivo}</strong>
                      <span className={`status-documento ${documento.status}`}>
                        {rotuloStatus(documento.status)}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="sem-documentos">Nenhum documento enviado ainda.</p>
            )}
          </section>
        </section>
      </main>
    )
  }

  return (
    <main className="pagina">
      <section className="marca">
        <div className="logo">◉ NOCTUA</div>
        <div className="texto-marca">
          <p>BASE DE CONHECIMENTO INTELIGENTE</p>
          <h1>Conhecimento seguro,<br />rápido e fácil.</h1>
          <span>Centralize documentos e encontre respostas fundamentadas nas fontes da sua organização.</span>
        </div>
        <b>+</b>
      </section>

      <section className="acesso">
        <div className="cartao">
          <p className="etiqueta">AGENTE NOCTUA</p>
          <h2>{cadastro ? 'Crie sua conta' : 'Boas-vindas de volta'}</h2>
          <div className="abas">
            <button
              type="button"
              className={!cadastro ? 'ativo' : ''}
              onClick={() => { navegar('/login'); setEstado('neutro') }}
            >
              Entrar
            </button>
            <button
              type="button"
              className={cadastro ? 'ativo' : ''}
              onClick={() => { navegar('/cadastro'); setEstado('neutro') }}
            >
              Criar conta
            </button>
          </div>
          <form onSubmit={entrar}>
            {cadastro && (
              <label>
                Organização
                <input name="organizacao" required placeholder="Ex.: Noctua Tecnologia" />
              </label>
            )}
            <label>
              E-mail
              <input name="email" type="email" required placeholder="voce@organizacao.com" />
            </label>
            <label>
              Senha
              <span className="campo-senha">
                <input
                  name="senha"
                  type={senhaVisivel ? 'text' : 'password'}
                  minLength={8}
                  required
                  placeholder="Mínimo de 8 caracteres"
                />
                <button
                  type="button"
                  aria-label={senhaVisivel ? 'Ocultar senha' : 'Mostrar senha'}
                  aria-pressed={senhaVisivel}
                  onClick={() => setSenhaVisivel(!senhaVisivel)}
                >
                  {senhaVisivel ? 'Ocultar' : 'Mostrar'}
                </button>
              </span>
            </label>
            <button className="principal" disabled={estado === 'carregando'}>
              {estado === 'carregando' ? 'Aguarde…' : cadastro ? 'Criar conta' : 'Entrar no Noctua'}
            </button>
          </form>
          {aviso}
        </div>
      </section>
    </main>
  )
}
