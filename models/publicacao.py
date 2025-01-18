from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .album import Album
    from .perfil import Perfil


class PubAlbum(SQLModel, table=True):
    pub_id: int | None = Field(default=None, foreign_key="publicacao.id",
                               primary_key=True)
    album_id: int | None = Field(default=None, foreign_key="album.id",
                                 primary_key=True)


class PublicacaoBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    legenda: str | None = Field(default=None)
    curtidas: int | None = Field(default=0)
    data_criacao: datetime | None = Field(default_factory=lambda:
                               datetime.now(timezone.utc))
    caminho_imagem: str


class Publicacao(PublicacaoBase, table=True):
    perfil_id: int = Field(foreign_key='perfil.id')
    perfil: 'Perfil' = Relationship(back_populates='publicacoes')
    albuns: list["Album"] = Relationship(back_populates="publicacoes",
                                         link_model=PubAlbum)


class PubCompleta(PublicacaoBase):
    user: 'Perfil'
    albuns: list['Album'] = None
