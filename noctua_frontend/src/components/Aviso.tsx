import { Estado } from '../tipos'

type PropsAviso = {
  estado: Estado
  mensagem: string
}

export function Aviso({ estado, mensagem }: PropsAviso) {
  if (estado === 'neutro') return null

  return (
    <p className={`aviso ${estado}`} role={estado === 'erro' ? 'alert' : 'status'}>
      {mensagem}
    </p>
  )
}
