from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .perfil import Perfil
    from .album import Album

class PublicacaoBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)

class Publicacao(PublicacaoBase, table=True):
    nome: str
    perfil_id: int | None = Field(default=None, foreign_key='perfil.id')
    perfil: 'Perfil' = Relationship(back_populates='publicacoes')
