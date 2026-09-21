from pydantic import BaseModel, Field


class CadastroUsuario(BaseModel):
    """Dados para criação de uma organização e seu primeiro usuário."""

    nome_organizacao: str = Field(min_length=2, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    senha: str = Field(min_length=8, max_length=128)


class CredenciaisUsuario(BaseModel):
    """Credenciais usadas para autenticação."""

    email: str = Field(min_length=3, max_length=255)
    senha: str = Field(min_length=8, max_length=128)


class TokenAcesso(BaseModel):
    """Token JWT retornado após cadastro ou login."""

    access_token: str
    token_type: str = "bearer"
