const api = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

type OpcoesRequisicao = RequestInit & {
  aoNaoAutorizado?: () => void
}

export function cabecalhosAutorizacao() {
  return { Authorization: `Bearer ${sessionStorage.getItem('noctua_token')}` }
}

export async function requisitarApi<T>(caminho: string, opcoes: OpcoesRequisicao = {}): Promise<T> {
  const { aoNaoAutorizado, ...opcoesFetch } = opcoes
  const resposta = await fetch(`${api}${caminho}`, opcoesFetch)
  const corpo = await resposta.json().catch(() => ({})) as T & { detail?: string }

  if (resposta.status === 401) aoNaoAutorizado?.()
  if (!resposta.ok) throw new Error(corpo.detail || 'Não foi possível concluir a solicitação.')

  return corpo
}
