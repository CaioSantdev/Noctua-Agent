from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.seguranca import obter_usuario_id_do_token
from app.infrastructure.banco import obter_sessao
from app.models.usuario import Usuario
from app.repositories.repositorio_usuario import RepositorioUsuario

esquema_bearer = HTTPBearer()


def obter_usuario_autenticado(
    credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer),
    sessao: Session = Depends(obter_sessao),
) -> Usuario:
    """Obtém o usuário validado pelo JWT enviado no cabeçalho Bearer."""
    try:
        usuario_id = obter_usuario_id_do_token(credenciais.credentials)
    except (RuntimeError, ValueError) as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from erro

    usuario = RepositorioUsuario(sessao).obter_por_id(usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario
