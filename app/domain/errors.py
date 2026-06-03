class DomainError(Exception):
    pass


class FigurinhaNaoEncontrada(DomainError):
    def __init__(self) -> None:
        super().__init__("figurinha não encontrado")


class CampoObrigatorio(DomainError):
    def __init__(self, campo: str) -> None:
        super().__init__(f"o campo '{campo}' é obrigatório")


class TipoInvalido(DomainError):
    def __init__(self, validos: list[str]) -> None:
        super().__init__(f"tipo inválido; valores aceitos: {', '.join(validos)}")


class PosicaoInvalida(DomainError):
    def __init__(self, validos: list[str]) -> None:
        super().__init__(f"posição inválida; valores aceitos: {', '.join(validos)}")
