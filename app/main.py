from fastapi import FastAPI

from app.handler.figure_handler import FigureHandler, registrar_tratadores_de_erro
from app.repository.database import (
    criar_engine,
    criar_fabrica_de_sessao,
    criar_tabelas,
)
from app.repository.figure_repository import SqlAlchemyFigureRepository
from app.service.figure_service import FigureServiceImpl

URL_DO_BANCO = "sqlite:///figurinhas.db"


def criar_aplicacao() -> FastAPI:
    engine = criar_engine(URL_DO_BANCO)
    criar_tabelas(engine)
    fabrica_de_sessao = criar_fabrica_de_sessao(engine)

    repositorio = SqlAlchemyFigureRepository(fabrica_de_sessao)
    servico = FigureServiceImpl(repositorio)
    handler = FigureHandler(servico)

    app = FastAPI(title="API de Figurinhas da Copa do Mundo 2026")
    app.include_router(handler.router)
    registrar_tratadores_de_erro(app)
    return app


app = criar_aplicacao()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
