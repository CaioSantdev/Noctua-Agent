from app.core.seguranca import criar_token_acesso, gerar_hash_senha, verificar_senha
from app.models.organizacao import Organizacao
from app.models.usuario import Usuario
from app.repositories.repositorio_organizacao import RepositorioOrganizacao
from app.repositories.repositorio_usuario import RepositorioUsuario


class ErroAutenticacao(ValueError):
    """Indica credenciais ou dados de cadastro inválidos."""


class ServicoAutenticacao:
    """Orquestra cadastro, autenticação e emissão de tokens."""

    def __init__(
        self,
        repositorio_organizacao: RepositorioOrganizacao,
        repositorio_usuario: RepositorioUsuario,
    ) -> None:
        self.repositorio_organizacao = repositorio_organizacao
        self.repositorio_usuario = repositorio_usuario

    def cadastrar(self, nome_organizacao: str, email: str, senha: str) -> str:
        """Cria organização e primeiro usuário, retornando seu token."""
        email_normalizado = email.strip().lower()
        if self.repositorio_usuario.obter_por_email(email_normalizado):
            raise ErroAutenticacao("Já existe um usuário com este e-mail.")
        organizacao = self.repositorio_organizacao.adicionar(Organizacao(nome=nome_organizacao.strip()))
        usuario = self.repositorio_usuario.adicionar(
            Usuario(
                organizacao_id=organizacao.id,
                email=email_normalizado,
                senha_hash=gerar_hash_senha(senha),
            )
        )
        return criar_token_acesso(usuario)

    def autenticar(self, email: str, senha: str) -> str:
        """Valida credenciais e retorna um novo token de acesso."""
        usuario = self.repositorio_usuario.obter_por_email(email.strip().lower())
        if usuario is None or not verificar_senha(senha, usuario.senha_hash):
            raise ErroAutenticacao("E-mail ou senha inválidos.")
        return criar_token_acesso(usuario)
