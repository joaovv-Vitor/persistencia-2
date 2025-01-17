from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models.publicacao import PubAlbum

router = APIRouter(
    prefix='/pubAlbum',
    tags=['PubAlbum']
)


@router.post('/', response_model=PubAlbum)
def create_pubAlbum(pubAlbum: PubAlbum, session: Session = Depends(get_session)):
    session.add(pubAlbum)
    session.commit()
    session.refresh(pubAlbum)
    return pubAlbum


@router.get('/', response_model=list[PubAlbum])  # listar pubAlbum
def read_pubAlbum(offset: int = 0, limit: int = Query(default=10, le=100),
               session: Session = Depends(get_session)):
    return session.exec(select(PubAlbum).offset(offset).limit(limit)).all()


@router.get('/{pub_id}/{album_id}', response_model=PubAlbum)  # Corrigido a rota para ter ambos os IDs
def read_pubAlbuns(pub_id: int, album_id: int, session: Session = Depends(get_session)):
    # Buscar o PubAlbum usando ambos os IDs
    pub_album = session.exec(select(PubAlbum).where(PubAlbum.pub_id == pub_id, PubAlbum.album_id == album_id)).first()

    # Verificar se não encontrou o PubAlbum
    if not pub_album:
        raise HTTPException(status_code=404, detail='PubAlbum não encontrado')

    return pub_album


@router.put('/{pub_id}/{album_id}', response_model=PubAlbum)
def update_pubAlbum(pub_id: int, album_id: int, pub_album: PubAlbum, session: Session = Depends(get_session)):
    # Buscar o PubAlbum existente com base nos dois IDs
    existing_pub_album = session.exec(select(PubAlbum).where(PubAlbum.pub_id == pub_id, PubAlbum.album_id == album_id)).first()

    if not existing_pub_album:
        raise HTTPException(status_code=404, detail='PubAlbum não encontrado')

    # Atualizar os campos do PubAlbum com os dados fornecidos no corpo da requisição usando model_dump()
    pub_album_data = pub_album.model_dump(exclude_unset=True)
    for field, value in pub_album_data.items():
        setattr(existing_pub_album, field, value)

    # Commit da alteração
    session.commit()
    session.refresh(existing_pub_album)

    return existing_pub_album


@router.delete('/{pub_id}/{album_id}')
def delete_pubAlbum(pub_id: int, album_id: int, session: Session = Depends(get_session)):
    # Buscar o PubAlbum existente com base nos dois IDs
    existing_pub_album = session.exec(select(PubAlbum).where(PubAlbum.pub_id == pub_id, PubAlbum.album_id == album_id)).first()

    if not existing_pub_album:
        raise HTTPException(status_code=404, detail='PubAlbum não encontrado')

    # Deletar o PubAlbum encontrado
    session.delete(existing_pub_album)
    session.commit()

    return {'ok': True}
