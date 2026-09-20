import { FormEvent, useState } from 'react'

const api = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function App() {
  const [cadastro, setCadastro] = useState(false)
  const [erro, setErro] = useState('')

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault(); setErro('')
    const dados = new FormData(evento.currentTarget)
    const corpo = cadastro ? { nome_organizacao: dados.get('organizacao'), email: dados.get('email'), senha: dados.get('senha') } : { email: dados.get('email'), senha: dados.get('senha') }
    try {
      const resposta = await fetch(`${api}${cadastro ? '/auth/register' : '/auth/login'}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(corpo) })
      const json = await resposta.json()
      if (!resposta.ok) throw new Error(json.detail)
      sessionStorage.setItem('noctua_token', json.access_token)
      setErro('Acesso realizado. O dashboard será concluído na próxima etapa.')
    } catch (causa) { setErro(causa instanceof Error ? causa.message : 'Não foi possível conectar à API.') }
  }

  return <main className="pagina"><section className="marca"><div className="logo">◉ NOCTUA</div><div className="texto-marca"><p>BASE DE CONHECIMENTO INTELIGENTE</p><h1>Conhecimento seguro,<br />perto de você.</h1><span>Centralize documentos e encontre respostas fundamentadas nas fontes da sua organização.</span></div><b>+</b></section><section className="acesso"><div className="cartao"><p className="etiqueta">PORTAL NOCTUA</p><h2>{cadastro ? 'Crie sua conta' : 'Boas-vindas de volta'}</h2><p>{cadastro ? 'Comece a organizar o conhecimento do seu time.' : 'Acesse a base de conhecimento da sua organização.'}</p><div className="abas"><button className={!cadastro ? 'ativo' : ''} onClick={() => setCadastro(false)}>Entrar</button><button className={cadastro ? 'ativo' : ''} onClick={() => setCadastro(true)}>Criar conta</button></div><form onSubmit={enviar}>{cadastro && <label>Nome da organização<input name="organizacao" required placeholder="Ex.: Noctua Tecnologia" /></label>}<label>E-mail<input name="email" type="email" required placeholder="voce@organizacao.com" /></label><label>Senha<input name="senha" type="password" minLength={8} required placeholder="Mínimo de 8 caracteres" /></label><button className="principal">{cadastro ? 'Criar conta' : 'Entrar no Noctua'} <span>→</span></button></form>{erro && <small>{erro}</small>}</div></section></main>
}
