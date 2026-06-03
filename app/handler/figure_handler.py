from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.dto import CreateFigureRequest, FigureResponse, UpdateFigureRequest
from app.domain.errors import DomainError, FigurinhaNaoEncontrada
from app.domain.figurinha import Figurinha
from app.service.figure_service import FigureService


class FigureHandler:
    def __init__(self, servico: FigureService) -> None:
        self._servico = servico
        self.router = APIRouter(prefix="/figurinha", tags=["figurinha"])
        self._registrar_rotas()

    def _registrar_rotas(self) -> None:
        self.router.add_api_route(
            "", self.criar, methods=["POST"], status_code=201,
            response_model=FigureResponse,
        )
        self.router.add_api_route(
            "", self.listar, methods=["GET"],
            response_model=list[FigureResponse],
        )
        self.router.add_api_route(
            "/{figurinha_id}", self.buscar, methods=["GET"],
            response_model=FigureResponse,
        )
        self.router.add_api_route(
            "/{figurinha_id}", self.atualizar, methods=["PUT"],
            response_model=FigureResponse,
        )
        self.router.add_api_route(
            "/{figurinha_id}", self.remover, methods=["DELETE"], status_code=204,
        )

    def criar(self, req: CreateFigureRequest) -> FigureResponse:
        figurinha = self._servico.create_figurinha(req)
        return self._para_resposta(figurinha)

    def listar(
        self,
        posicao: str | None = None,
        tipo: str | None = None,
    ) -> list[FigureResponse]:
        figurinhas = self._servico.list_figurinhas(tipo=tipo, posicao=posicao)
        return [self._para_resposta(figurinha) for figurinha in figurinhas]

    def buscar(self, figurinha_id: int) -> FigureResponse:
        figurinha = self._servico.get_figurinha(figurinha_id)
        return self._para_resposta(figurinha)

    def atualizar(
        self, figurinha_id: int, req: UpdateFigureRequest
    ) -> FigureResponse:
        figurinha = self._servico.update_figurinha(figurinha_id, req)
        return self._para_resposta(figurinha)

    def remover(self, figurinha_id: int) -> None:
        self._servico.delete_figurinha(figurinha_id)

    def _para_resposta(self, figurinha: Figurinha) -> FigureResponse:
        return FigureResponse.model_validate(figurinha)


def _status_do_erro(erro: DomainError) -> int:
    if isinstance(erro, FigurinhaNaoEncontrada):
        return 404
    return 400


def registrar_tratadores_de_erro(app: FastAPI) -> None:
    async def tratar_erro_de_dominio(_: Request, erro: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=_status_do_erro(erro),
            content={"error": str(erro)},
        )

    app.add_exception_handler(DomainError, tratar_erro_de_dominio)
