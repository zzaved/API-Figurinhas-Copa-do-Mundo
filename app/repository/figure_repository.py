from abc import ABC, abstractmethod

from sqlalchemy.orm import sessionmaker

from app.domain.enums import PosicaoFigurinha, TipoFigurinha
from app.domain.figurinha import Figurinha
from app.repository.models import FigurinhaModel


class FigureRepository(ABC):
    @abstractmethod
    def create(self, figurinha: Figurinha) -> Figurinha:
        ...

    @abstractmethod
    def find_all(
        self,
        tipo: TipoFigurinha | None = None,
        posicao: PosicaoFigurinha | None = None,
    ) -> list[Figurinha]:
        ...

    @abstractmethod
    def find_by_id(self, figurinha_id: int) -> Figurinha | None:
        ...

    @abstractmethod
    def update(self, figurinha: Figurinha) -> Figurinha:
        ...

    @abstractmethod
    def delete(self, figurinha_id: int) -> None:
        ...


class SqlAlchemyFigureRepository(FigureRepository):
    def __init__(self, fabrica_de_sessao: sessionmaker) -> None:
        self._fabrica_de_sessao = fabrica_de_sessao

    def create(self, figurinha: Figurinha) -> Figurinha:
        with self._fabrica_de_sessao() as sessao:
            modelo = self._para_modelo(figurinha)
            sessao.add(modelo)
            sessao.commit()
            sessao.refresh(modelo)
            return self._para_dominio(modelo)

    def find_all(
        self,
        tipo: TipoFigurinha | None = None,
        posicao: PosicaoFigurinha | None = None,
    ) -> list[Figurinha]:
        with self._fabrica_de_sessao() as sessao:
            consulta = sessao.query(FigurinhaModel)
            if tipo is not None:
                consulta = consulta.filter(FigurinhaModel.tipo == tipo.value)
            if posicao is not None:
                consulta = consulta.filter(FigurinhaModel.posicao == posicao.value)
            return [self._para_dominio(modelo) for modelo in consulta.all()]

    def find_by_id(self, figurinha_id: int) -> Figurinha | None:
        with self._fabrica_de_sessao() as sessao:
            modelo = sessao.get(FigurinhaModel, figurinha_id)
            if modelo is None:
                return None
            return self._para_dominio(modelo)

    def update(self, figurinha: Figurinha) -> Figurinha:
        with self._fabrica_de_sessao() as sessao:
            modelo = sessao.get(FigurinhaModel, figurinha.id)
            modelo.numero = figurinha.numero
            modelo.tipo = figurinha.tipo.value
            modelo.posicao = figurinha.posicao.value
            modelo.updated_at = figurinha.updated_at
            sessao.commit()
            sessao.refresh(modelo)
            return self._para_dominio(modelo)

    def delete(self, figurinha_id: int) -> None:
        with self._fabrica_de_sessao() as sessao:
            modelo = sessao.get(FigurinhaModel, figurinha_id)
            sessao.delete(modelo)
            sessao.commit()

    def _para_modelo(self, figurinha: Figurinha) -> FigurinhaModel:
        return FigurinhaModel(
            id=figurinha.id,
            numero=figurinha.numero,
            tipo=figurinha.tipo.value,
            posicao=figurinha.posicao.value,
            created_at=figurinha.created_at,
            updated_at=figurinha.updated_at,
        )

    def _para_dominio(self, modelo: FigurinhaModel) -> Figurinha:
        return Figurinha(
            id=modelo.id,
            numero=modelo.numero,
            tipo=TipoFigurinha(modelo.tipo),
            posicao=PosicaoFigurinha(modelo.posicao),
            created_at=modelo.created_at,
            updated_at=modelo.updated_at,
        )
