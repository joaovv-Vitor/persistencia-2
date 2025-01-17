from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from models.album import Album
from database import get_session

router = APIRouter(
    prefix="/album",  # Prefixo para todas as rotas
    tags=["Album"],   # Tag para documentação automática
)


@router.post("/", response_model=Album)
def create_album(album: Album, session: Session = Depends(get_session)):
    session.add(album)
    session.commit()
    session.refresh(album)
    return album