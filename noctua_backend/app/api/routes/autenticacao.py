from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.banco import obter_sessao
from app.repositories.repositorio_organizacao import RepositorioOrganizacao
from app.repositories.repositorio_usuario import RepositorioUsuario
from app.schemas.autenticacao import CadastroUsuario, CredenciaisUsuario, TokenAcesso
from app.services.servico_autenticacao import ErroAutenticacao, ServicoAutenticacao

roteador = APIRouter(prefix="/auth", tags=["autenticação"])


def obter_servico_autenticacao(sessao: Session = Depends(obter_sessao)) -> ServicoAutenticacao:
    """Monta o serviço de autenticação para a requisição atual."""
    return ServicoAutenticacao(RepositorioOrganizacao(sessao), RepositorioUsuario(sessao))


@roteador.post("/register", response_model=TokenAcesso, status_code=status.HTTP_201_CREATED)
async def cadastrar(
    dados: CadastroUsuario,
    servico: ServicoAutenticacao = Depends(obter_servico_autenticacao),
) -> TokenAcesso:
    """Cadastra uma organização e seu primeiro usuário."""
    try:
        return TokenAcesso(access_token=servico.cadastrar(**dados.model_dump()))
    except ErroAutenticacao as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro)) from erro


@roteador.post("/login", response_model=TokenAcesso)
async def entrar(
    dados: CredenciaisUsuario,
    servico: ServicoAutenticacao = Depends(obter_servico_autenticacao),
) -> TokenAcesso:
    """Autentica usuário e retorna JWT de curta duração."""
    try:
        return TokenAcesso(access_token=servico.autenticar(**dados.model_dump()))
    except ErroAutenticacao as erro:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(erro)) from erro
