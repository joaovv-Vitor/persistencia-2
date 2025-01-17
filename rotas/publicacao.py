from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from models.publicacao import Publicacao
from database import get_session


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