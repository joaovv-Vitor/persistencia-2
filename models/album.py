from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .publicacao import PubAlbum, Publicacao

if TYPE_CHECKING:
    from .perfil import Perfil, PerfilBase


class AlbumBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True, index=True)
    nome: str
    capa: str


class Album(AlbumBase, table=True):
    perfil_id: int | None = Field(default=None, foreign_key='perfil.id')
    perfil: 'Perfil' = Relationship(back_populates='albuns')
    publicacoes: list["Publicacao"] = Relationship(back_populates="albuns",
                                                   link_model=PubAlbum)
    
class AlbumUser(AlbumBase):
    perfil: 'PerfilBase'