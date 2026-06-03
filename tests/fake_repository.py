from app.domain.enums import PosicaoFigurinha, TipoFigurinha
from app.domain.figurinha import Figurinha
from app.repository.figure_repository import FigureRepository


class FakeFigureRepository(FigureRepository):
    def __init__(self) -> None:
        self._figurinhas: dict[int, Figurinha] = {}
        self._proximo_id = 1

    def create(self, figurinha: Figurinha) -> Figurinha:
        figurinha.id = self._proximo_id
        self._figurinhas[self._proximo_id] = figurinha
        self._proximo_id += 1
        return figurinha

    def find_all(
        self,
        tipo: TipoFigurinha | None = None,
        posicao: PosicaoFigurinha | None = None,
    ) -> list[Figurinha]:
        resultado = list(self._figurinhas.values())
        if tipo is not None:
            resultado = [f for f in resultado if f.tipo == tipo]
        if posicao is not None:
            resultado = [f for f in resultado if f.posicao == posicao]
        return resultado

    def find_by_id(self, figurinha_id: int) -> Figurinha | None:
        return self._figurinhas.get(figurinha_id)

    def update(self, figurinha: Figurinha) -> Figurinha:
        self._figurinhas[figurinha.id] = figurinha
        return figurinha

    def delete(self, figurinha_id: int) -> None:
        self._figurinhas.pop(figurinha_id, None)
