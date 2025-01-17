from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models.perfil import Perfil

router = APIRouter(
    prefix='/perfil',  # Prefixo para todas as rotas
    tags=['Perfil'],   # Tag para documentação automática
)


@router.post('/', response_model=Perfil)  # criar perfil
def create_perfil(perfil: Perfil, session: Session = Depends(get_session)):
    session.add(perfil)
    session.commit()
    session.refresh(perfil)
    return perfil


@router.get('/', response_model=list[Perfil])  # listar perfis
def read_perfis(offset: int = 0, limit: int = Query(default=10, le=100),
               session: Session = Depends(get_session)):
    return session.exec(select(Perfil).offset(offset).limit(limit)).all()


@router.get('/{perfil_id}', response_model=Perfil)  # listar perfis pelo id
def read_perfis(perfil_id: int, session: Session = Depends(get_session)):
    perfil = session.get(Perfil, perfil_id)
    if not perfil:
        raise HTTPException(status_code=404, detail='Perfil não encontrado')
    return perfil


@router.put('/{perfil_id}', response_model=Perfil)
def update_perfil(perfil_id: int, perfil_db: Perfil, session: Session = Depends(get_session)):
    perfil = session.get(Perfil, perfil_id)
    if not perfil:
        raise HTTPException(status_code=404, detail='Perfil não encontrado')

    for field, value in perfil_db.model_dump(exclude_unset=True).items():
        setattr(perfil, field, value)

    session.commit()
    session.refresh(perfil)
    return perfil


@router.delete('/{perfil_id}')
def delete_perfil(perfil_id: int, session: Session = Depends(get_session)):
    perfil = session.get(Perfil, perfil_id)
    if not perfil:
        raise HTTPException(status_code=404, detail='Perfil não encontrado')
    session.delete(perfil)
    session.commit()
    return {'ok': True}
