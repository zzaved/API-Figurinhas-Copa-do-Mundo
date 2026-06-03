from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def criar_engine(url: str) -> Engine:
    return create_engine(url)


def criar_fabrica_de_sessao(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, expire_on_commit=False)


def criar_tabelas(engine: Engine) -> None:
    Base.metadata.create_all(engine)
