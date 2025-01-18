from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models.album import Album
from models.publicacao import PubAlbum, Publicacao
from models.perfil import Perfil

router = APIRouter(
    prefix="/album",  # Prefixo para todas as rotas
    tags=["Album"],   # Tag para documentação automática
)


# @router.post('/', response_model=Album)
# def create_album(album: Album, session: Session = Depends(get_session)):
#     session.add(album)
#     session.commit()
#     session.refresh(album)
#     return album

@router.post('/', response_model=Album)
def create_album(album: Album, session: Session = Depends(get_session)):

    idvalid = session.exec(select(Perfil).where(Perfil.id == album.perfil_id)).first()

    if not idvalid:  # Caso o perfil nao exista
        raise HTTPException(status_code=400, detail='Perfil não encontrado.')


    session.add(album)
    session.commit()
    session.refresh(album)
    return album




@router.get('/', response_model=list[Album])
def read_albuns(offset: int = 0, limit: int = Query(default=10, le=100),
               session: Session = Depends(get_session)):
    return session.exec(select(Album).offset(offset).limit(limit)).all()


@router.get('/{album_id}', response_model=Album)
def read_albuns(album_id: int, session: Session = Depends(get_session)):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album não encontrado.")
    return album


@router.put('/{album_id}', response_model=Album)
def update_album(album_id: int, album_db: Album, session: Session = Depends(get_session)):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album não encontrado.")

    for field, value in album_db.model_dump(exclude_unset=True).items():
        setattr(album, field, value)

    session.commit()
    session.refresh(album)
    return album


@router.delete('/{album_id}')
def delete_album(album_id: int, session: Session = Depends(get_session)):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail='Album não encontrado.')
    session.delete(album)
    session.commit()
    return {'ok': True}


# listar todos os albuns de um determinado perfil
@router.get('/perfis/{perfil_id}/albuns', response_model=list[Album])
def listar_albuns(perfil_id: int, offset: int = 0, limit: int = Query(default=10, le=100),
                  session: Session = Depends(get_session)):
    # Criar consulta para buscar álbuns do perfil especificado com offset e limite
    albuns = select(Album).where(Album.perfil_id == perfil_id).offset(offset).limit(limit)
    resultados = session.exec(albuns).all()  # Executar a consulta

    # Verificar se nenhum álbum foi encontrado
    if not resultados:
        raise HTTPException(status_code=404, detail='Nenhum álbum encontrado para este perfil.')

    return resultados


@router.get('/perfis/{album_nome}/albuns', response_model=list[Album])
def listar_publicacoes_de_album(album_nome: str, offset: int = 0, limit: int = Query(default=10, le=100),
                  session: Session = Depends(get_session)):

    publicacoes = select(Album, Publicacao, PubAlbum).where(Album.publicacoes == PubAlbum.album_id).where(Publicacao.albuns == PubAlbum.pub_id).where(Album.nome == album_nome).offset(offset).limit(limit)
    resultados = session.exec(publicacoes).all()  # Executar a consulta

    # Verificar se nenhum álbum foi encontrado
    if not resultados:
        raise HTTPException(status_code=404, detail='Nenhum álbum encontrado para este perfil.')

    return resultados
