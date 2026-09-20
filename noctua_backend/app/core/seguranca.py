import base64
import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import obter_configuracoes
from app.models.usuario import Usuario

ALGORITMO_JWT = "HS256"


def gerar_hash_senha(senha: str) -> str:
    """Gera hash scrypt com salt aleatório para uma senha."""
    salt = secrets.token_bytes(16)
    parametros = (2**14, 8, 1)
    derivada = hashlib.scrypt(senha.encode(), salt=salt, n=parametros[0], r=parametros[1], p=parametros[2])
    salt_codificado = base64.b64encode(salt).decode()
    hash_codificado = base64.b64encode(derivada).decode()
    return f"scrypt${parametros[0]}${parametros[1]}${parametros[2]}${salt_codificado}${hash_codificado}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Compara uma senha com hash scrypt sem expor diferenças de tempo."""
    try:
        algoritmo, n, r, p, salt_codificado, hash_codificado = senha_hash.split("$")
        if algoritmo != "scrypt":
            return False
        salt = base64.b64decode(salt_codificado)
        esperado = base64.b64decode(hash_codificado)
        calculado = hashlib.scrypt(senha.encode(), salt=salt, n=int(n), r=int(r), p=int(p))
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(calculado, esperado)


def criar_token_acesso(usuario: Usuario) -> str:
    """Assina um JWT contendo somente identidade e organização do usuário."""
    configuracoes = obter_configuracoes()
    if not configuracoes.segredo_jwt:
        raise RuntimeError("JWT_SECRET não foi configurada no backend.")
    expiracao = datetime.now(UTC) + timedelta(minutes=configuracoes.expiracao_token_minutos)
    return jwt.encode(
        {"sub": str(usuario.id), "organizacao_id": str(usuario.organizacao_id), "exp": expiracao},
        configuracoes.segredo_jwt,
        algorithm=ALGORITMO_JWT,
    )


def obter_usuario_id_do_token(token: str) -> uuid.UUID:
    """Valida token e retorna o identificador do usuário autenticado."""
    configuracoes = obter_configuracoes()
    if not configuracoes.segredo_jwt:
        raise RuntimeError("JWT_SECRET não foi configurada no backend.")
    try:
        dados = jwt.decode(token, configuracoes.segredo_jwt, algorithms=[ALGORITMO_JWT])
        return uuid.UUID(dados["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as erro:
        raise ValueError("Token de acesso inválido ou expirado.") from erro
