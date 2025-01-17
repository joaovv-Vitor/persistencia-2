from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .perfil import Perfil
    from .publicacao import Publicacao


class AlbumBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True, index=True)
    nome: str
    capa: str

class Album(AlbumBase, table=True):
    perfil_id: int | None = Field(default=None, foreign_key='perfil.id')
    perfil: 'Perfil' = Relationship(back_populates='albuns')
    
