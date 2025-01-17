from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from models.perfil import Perfil
from database import get_session

router = APIRouter(
    prefix="/perfil",  # Prefixo para todas as rotas
    tags=["Perfil"],   # Tag para documentação automática
)


@router.post("/", response_model=Perfil)
def create_perfil(perfil: Perfil, session: Session = Depends(get_session)):
    session.add(perfil)
    session.commit()
    session.refresh(perfil)
    return perfil