import { ChangeEvent, FormEvent, KeyboardEvent, useEffect, useState } from 'react'

import { Acesso } from './pages/Acesso'
import { Dashboard } from './pages/Dashboard'
import { cabecalhosAutorizacao, requisitarApi } from './services/api'
import { Documento, Fonte, ModoDashboard, Rota } from './tipos'

function mensagemErro(valor: unknown, fallback: string) {
  return valor instanceof Error ? valor.message : fallback
}

function obterRota(caminho: string): Rota {
  return caminho === '/cadastro' || caminho === '/dashboard' ? caminho : '/login'
}

export default function App() {
  const [autenticado, setAutenticado] = useState(Boolean(sessionStorage.getItem('noctua_token')))
  const [rota, setRota] = useState<Rota>(() => obterRota(window.location.pathname))
  const [modo, setModo] = useState<ModoDashboard>('enviar')
  const [senhaVisivel, setSenhaVisivel] = useState(false)
  const [documentos, setDocumentos] = useState<Documento[]>([])
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [pergunta, setPergunta] = useState('')
  const [resposta, setResposta] = useState('')
  const [fontes, setFontes] = useState<Fonte[]>([])
  const [estado, setEstado] = useState<'neutro' | 'carregando' | 'sucesso' | 'erro'>('neutro')
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

  async function carregarDocumentos(exibirCarregamento = true) {
    if (exibirCarregamento) setCarregandoDocumentos(true)
    try {
      const lista = await requisitarApi<Documento[]>('/documents', {
        headers: cabecalhosAutorizacao(),
        aoNaoAutorizado: encerrarSessao,
      })
      setDocumentos(lista)
    } catch (erro) {
      if (exibirCarregamento) {
        setEstado('erro')
        setMensagem(mensagemErro(erro, 'Não foi possível carregar os documentos.'))
      }
    } finally {
      if (exibirCarregamento) setCarregandoDocumentos(false)
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

  useEffect(() => {
    if (autenticado) void carregarDocumentos()
  }, [autenticado])

  const possuiDocumentosEmProcessamento = documentos.some(documento => (
    documento.status === 'pending' || documento.status === 'processing'
  ))

  useEffect(() => {
    if (!autenticado || !possuiDocumentosEmProcessamento) return

    void carregarDocumentos(false)
    const intervalo = window.setInterval(() => void carregarDocumentos(false), 3000)
    return () => window.clearInterval(intervalo)
  }, [autenticado, possuiDocumentosEmProcessamento])

  async function entrar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setEstado('carregando')
    setMensagem(cadastro ? 'Criando sua conta…' : 'Entrando…')

    const formulario = new FormData(evento.currentTarget)
    const corpo = cadastro
      ? { nome_organizacao: formulario.get('organizacao'), email: formulario.get('email'), senha: formulario.get('senha') }
      : { email: formulario.get('email'), senha: formulario.get('senha') }

    try {
      const respostaApi = await requisitarApi<{ access_token: string }>(cadastro ? '/auth/register' : '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(corpo),
      })
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
      await requisitarApi('/documents', {
        method: 'POST',
        headers: cabecalhosAutorizacao(),
        body: formulario,
        aoNaoAutorizado: encerrarSessao,
      })
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
      const respostaApi = await requisitarApi<{ answer: string; sources: Fonte[] }>('/chat', {
        method: 'POST',
        headers: { ...cabecalhosAutorizacao(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: pergunta.trim() }),
        aoNaoAutorizado: encerrarSessao,
      })
      setResposta(respostaApi.answer)
      setFontes(respostaApi.sources)
      setEstado('sucesso')
      setMensagem('Resposta encontrada.')
    } catch (erro) {
      setEstado('erro')
      setMensagem(mensagemErro(erro, 'Falha ao consultar a base.'))
    }
  }

  function alterarArquivo(evento: ChangeEvent<HTMLInputElement>) {
    setArquivo(evento.target.files?.[0] ?? null)
  }

  function alterarPergunta(evento: ChangeEvent<HTMLInputElement>) {
    setPergunta(evento.target.value)
  }

  function enviarAoPressionarEnter(evento: KeyboardEvent<HTMLInputElement>) {
    if (evento.key === 'Enter') void perguntar()
  }

  if (autenticado) {
    return (
      <Dashboard
        modo={modo}
        arquivo={arquivo}
        pergunta={pergunta}
        resposta={resposta}
        fontes={fontes}
        documentos={documentos}
        estado={estado}
        mensagem={mensagem}
        carregandoDocumentos={carregandoDocumentos}
        aoSair={encerrarSessao}
        aoSelecionarEnvio={selecionarEnvio}
        aoSelecionarChat={selecionarChat}
        aoSelecionarArquivo={alterarArquivo}
        aoEnviarArquivo={enviarArquivo}
        aoAlterarPergunta={alterarPergunta}
        aoPressionarTecla={enviarAoPressionarEnter}
        aoPerguntar={perguntar}
      />
    )
  }

  return (
    <Acesso
      cadastro={cadastro}
      senhaVisivel={senhaVisivel}
      estado={estado}
      mensagem={mensagem}
      aoEntrar={entrar}
      aoIrParaLogin={() => {
        navegar('/login')
        setEstado('neutro')
      }}
      aoIrParaCadastro={() => {
        navegar('/cadastro')
        setEstado('neutro')
      }}
      aoAlternarSenha={() => setSenhaVisivel(!senhaVisivel)}
    />
  )
}
