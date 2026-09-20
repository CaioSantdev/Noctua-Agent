from typing import Literal

from pydantic import BaseModel


class RespostaSaude(BaseModel):
    """Resposta do endpoint de disponibilidade."""

    status: Literal["ok"]
