export type Documento = {
  id: string
  nome_arquivo: string
  status: string
}

export type Fonte = {
  document: string
  page: number | null
  excerpt: string
}

export type Estado = 'neutro' | 'carregando' | 'sucesso' | 'erro'
export type ModoDashboard = 'enviar' | 'perguntar'
export type Rota = '/login' | '/cadastro' | '/dashboard'
