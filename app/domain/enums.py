from enum import Enum


class TipoFigurinha(str, Enum):
    COMUM = "comum"
    BRILHANTE = "brilhante"
    LEGENDS_OURO = "legends_ouro"
    LEGENDS_BRONZE = "legends_bronze"

    @classmethod
    def valores(cls) -> list[str]:
        return [item.value for item in cls]


class PosicaoFigurinha(str, Enum):
    GOLEIRO = "Goleiro"
    ZAGUEIRO = "Zagueiro"
    MEIO_CAMPISTA = "Meio-campista"
    ATACANTE = "Atacante"

    @classmethod
    def valores(cls) -> list[str]:
        return [item.value for item in cls]
