import { FormEvent } from 'react'

import { Aviso } from '../components/Aviso'
import { Estado } from '../tipos'
import '../styles/Login.css'

type PropsAcesso = {
  cadastro: boolean
  senhaVisivel: boolean
  estado: Estado
  mensagem: string
  aoEntrar: (evento: FormEvent<HTMLFormElement>) => void
  aoIrParaLogin: () => void
  aoIrParaCadastro: () => void
  aoAlternarSenha: () => void
}

export function Acesso({
  cadastro,
  senhaVisivel,
  estado,
  mensagem,
  aoEntrar,
  aoIrParaLogin,
  aoIrParaCadastro,
  aoAlternarSenha,
}: PropsAcesso) {
  return (
    <main className="pagina">
      <section className="marca">
        <div className="logo">
          <img src="/imagens/logo_noctua.png" alt="Logo Noctua" />
          <span>NOCTUA</span>
        </div>
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
            <button type="button" className={!cadastro ? 'ativo' : ''} onClick={aoIrParaLogin}>
              Entrar
            </button>
            <button type="button" className={cadastro ? 'ativo' : ''} onClick={aoIrParaCadastro}>
              Criar conta
            </button>
          </div>

          <form onSubmit={aoEntrar}>
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
                  onClick={aoAlternarSenha}
                >
                  {senhaVisivel ? 'Ocultar' : 'Mostrar'}
                </button>
              </span>
            </label>
            <button className="principal" disabled={estado === 'carregando'}>
              {estado === 'carregando' ? 'Aguarde…' : cadastro ? 'Criar conta' : 'Entrar no Noctua'}
            </button>
          </form>
          <Aviso estado={estado} mensagem={mensagem} />
        </div>
      </section>
    </main>
  )
}
