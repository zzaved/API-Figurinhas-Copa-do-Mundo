from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import PosicaoFigurinha, TipoFigurinha


@dataclass
class Figurinha:
    id: int | None
    numero: str
    tipo: TipoFigurinha
    posicao: PosicaoFigurinha
    created_at: datetime
    updated_at: datetime
