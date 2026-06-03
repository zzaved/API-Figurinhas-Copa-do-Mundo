import pytest

from app.domain.dto import CreateFigureRequest, UpdateFigureRequest
from app.domain.errors import (
    CampoObrigatorio,
    FigurinhaNaoEncontrada,
    PosicaoInvalida,
    TipoInvalido,
)
from app.service.figure_service import FigureServiceImpl
from tests.fake_repository import FakeFigureRepository


def criar_servico() -> FigureServiceImpl:
    return FigureServiceImpl(FakeFigureRepository())


def test_criar_figurinha_valida():
    servico = criar_servico()
    figurinha = servico.create_figurinha(
        CreateFigureRequest(numero="BRA 15", tipo="comum", posicao="Atacante")
    )
    assert figurinha.id == 1
    assert figurinha.numero == "BRA 15"
    assert figurinha.created_at == figurinha.updated_at


def test_criar_sem_campo_obrigatorio():
    servico = criar_servico()
    with pytest.raises(CampoObrigatorio):
        servico.create_figurinha(CreateFigureRequest(numero="BRA 15", tipo="comum"))


def test_criar_com_tipo_invalido():
    servico = criar_servico()
    with pytest.raises(TipoInvalido):
        servico.create_figurinha(
            CreateFigureRequest(numero="BRA 15", tipo="lendario", posicao="Atacante")
        )


def test_criar_com_posicao_invalida():
    servico = criar_servico()
    with pytest.raises(PosicaoInvalida):
        servico.create_figurinha(
            CreateFigureRequest(numero="BRA 15", tipo="comum", posicao="Tecnico")
        )


def test_buscar_id_inexistente():
    servico = criar_servico()
    with pytest.raises(FigurinhaNaoEncontrada):
        servico.get_figurinha(999)


def test_listar_com_filtro_de_posicao():
    servico = criar_servico()
    servico.create_figurinha(
        CreateFigureRequest(numero="BRA 15", tipo="comum", posicao="Atacante")
    )
    servico.create_figurinha(
        CreateFigureRequest(numero="ARG 10", tipo="brilhante", posicao="Meio-campista")
    )
    resultado = servico.list_figurinhas(posicao="Atacante")
    assert len(resultado) == 1
    assert resultado[0].numero == "BRA 15"


def test_listar_com_filtro_invalido():
    servico = criar_servico()
    with pytest.raises(TipoInvalido):
        servico.list_figurinhas(tipo="xpto")


def test_update_preserva_created_at():
    servico = criar_servico()
    criada = servico.create_figurinha(
        CreateFigureRequest(numero="BRA 15", tipo="comum", posicao="Atacante")
    )
    atualizada = servico.update_figurinha(
        criada.id,
        UpdateFigureRequest(numero="BRA 16", tipo="legends_ouro", posicao="Zagueiro"),
    )
    assert atualizada.created_at == criada.created_at
    assert atualizada.updated_at >= criada.updated_at
    assert atualizada.tipo.value == "legends_ouro"


def test_update_id_inexistente():
    servico = criar_servico()
    with pytest.raises(FigurinhaNaoEncontrada):
        servico.update_figurinha(
            999, UpdateFigureRequest(numero="X", tipo="comum", posicao="Goleiro")
        )


def test_delete_remove_a_figurinha():
    servico = criar_servico()
    criada = servico.create_figurinha(
        CreateFigureRequest(numero="BRA 15", tipo="comum", posicao="Atacante")
    )
    servico.delete_figurinha(criada.id)
    with pytest.raises(FigurinhaNaoEncontrada):
        servico.get_figurinha(criada.id)


def test_delete_id_inexistente():
    servico = criar_servico()
    with pytest.raises(FigurinhaNaoEncontrada):
        servico.delete_figurinha(999)
