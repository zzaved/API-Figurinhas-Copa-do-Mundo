from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import PosicaoFigurinha, TipoFigurinha


class CreateFigureRequest(BaseModel):
    numero: str | None = None
    tipo: str | None = None
    posicao: str | None = None


class UpdateFigureRequest(BaseModel):
    numero: str | None = None
    tipo: str | None = None
    posicao: str | None = None


class FigureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    tipo: TipoFigurinha
    posicao: PosicaoFigurinha
    created_at: datetime
    updated_at: datetime
