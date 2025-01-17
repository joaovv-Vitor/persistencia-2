from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.album import Album

router = APIRouter(
    prefix="/album",  # Prefixo para todas as rotas
    tags=["Album"],   # Tag para documentação automática
)


@router.post('/', response_model=Album)
def create_album(album: Album, session: Session = Depends(get_session)):
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
        raise HTTPException(status_code=404, detail="Album não encontrado")
    return album


@router.put('/{album_id}', response_model=Album)
def update_album(album_id: int, album_db: Album, session: Session = Depends(get_session)):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album não encontrado")
    
    for field, value in album_db.model_dump(exclude_unset=True).items():
        setattr(album, field, value)

    session.commit()
    session.refresh(album)
    return album


@router.delete('/{album_id}')
def delete_album(album_id: int, session: Session = Depends(get_session)):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail='Album não encontrado')
    session.delete(album)
    session.commit()
    return {'ok': True}