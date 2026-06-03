from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.dto import CreateFigureRequest, UpdateFigureRequest
from app.domain.enums import PosicaoFigurinha, TipoFigurinha
from app.domain.errors import (
    CampoObrigatorio,
    FigurinhaNaoEncontrada,
    PosicaoInvalida,
    TipoInvalido,
)
from app.domain.figurinha import Figurinha
from app.repository.figure_repository import FigureRepository


class FigureService(ABC):
    @abstractmethod
    def create_figurinha(self, req: CreateFigureRequest) -> Figurinha:
        ...

    @abstractmethod
    def list_figurinhas(
        self,
        tipo: str | None = None,
        posicao: str | None = None,
    ) -> list[Figurinha]:
        ...

    @abstractmethod
    def get_figurinha(self, figurinha_id: int) -> Figurinha:
        ...

    @abstractmethod
    def update_figurinha(
        self, figurinha_id: int, req: UpdateFigureRequest
    ) -> Figurinha:
        ...

    @abstractmethod
    def delete_figurinha(self, figurinha_id: int) -> None:
        ...


class FigureServiceImpl(FigureService):
    def __init__(self, repositorio: FigureRepository) -> None:
        self._repositorio = repositorio

    def create_figurinha(self, req: CreateFigureRequest) -> Figurinha:
        numero = self._exigir(req.numero, "numero")
        tipo = self._validar_tipo(self._exigir(req.tipo, "tipo"))
        posicao = self._validar_posicao(self._exigir(req.posicao, "posicao"))
        agora = datetime.now()
        figurinha = Figurinha(
            id=None,
            numero=numero,
            tipo=tipo,
            posicao=posicao,
            created_at=agora,
            updated_at=agora,
        )
        return self._repositorio.create(figurinha)

    def list_figurinhas(
        self,
        tipo: str | None = None,
        posicao: str | None = None,
    ) -> list[Figurinha]:
        tipo_filtro = self._validar_tipo(tipo) if tipo else None
        posicao_filtro = self._validar_posicao(posicao) if posicao else None
        return self._repositorio.find_all(tipo_filtro, posicao_filtro)

    def get_figurinha(self, figurinha_id: int) -> Figurinha:
        figurinha = self._repositorio.find_by_id(figurinha_id)
        if figurinha is None:
            raise FigurinhaNaoEncontrada()
        return figurinha

    def update_figurinha(
        self, figurinha_id: int, req: UpdateFigureRequest
    ) -> Figurinha:
        existente = self.get_figurinha(figurinha_id)
        numero = self._exigir(req.numero, "numero")
        tipo = self._validar_tipo(self._exigir(req.tipo, "tipo"))
        posicao = self._validar_posicao(self._exigir(req.posicao, "posicao"))
        atualizada = Figurinha(
            id=existente.id,
            numero=numero,
            tipo=tipo,
            posicao=posicao,
            created_at=existente.created_at,
            updated_at=datetime.now(),
        )
        return self._repositorio.update(atualizada)

    def delete_figurinha(self, figurinha_id: int) -> None:
        self.get_figurinha(figurinha_id)
        self._repositorio.delete(figurinha_id)

    def _exigir(self, valor: str | None, campo: str) -> str:
        if valor is None or valor.strip() == "":
            raise CampoObrigatorio(campo)
        return valor

    def _validar_tipo(self, valor: str) -> TipoFigurinha:
        try:
            return TipoFigurinha(valor)
        except ValueError:
            raise TipoInvalido(TipoFigurinha.valores()) from None

    def _validar_posicao(self, valor: str) -> PosicaoFigurinha:
        try:
            return PosicaoFigurinha(valor)
        except ValueError:
            raise PosicaoInvalida(PosicaoFigurinha.valores()) from None
