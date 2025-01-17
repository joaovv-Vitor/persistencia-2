from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .album import Album, AlbumBase
    from .publicacao import Publicacao, PublicacaoBase


class PerfilBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True, index=True)
    nome: str
    bio: str
    email: str = Field(unique=True)


class Perfil(PerfilBase, table=True):
    albuns: list["Album"] = Relationship(back_populates='perfil')
    publicacoes: list['Publicacao'] = Relationship(back_populates='perfil')

class PerfilCompleto(PerfilBase):
    albuns: list['AlbumBase']
    publicacoes: list['PublicacaoBase']
