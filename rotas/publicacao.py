from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_session
from models.publicacao import Publicacao

router = APIRouter(
    prefix='/publicacao',
    tags=['Publicacaoo']
)


@router.post("/", response_model=Publicacao)
def create_album(publicacao: Publicacao, session: Session = Depends(get_session)):
    session.add(publicacao)
    session.commit()
    session.refresh(publicacao)
    return publicacao
