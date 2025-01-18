from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session,select
from sqlalchemy.exc import SQLAlchemyError
from database import get_session
from datetime import datetime, timezone
from models.publicacao import Publicacao

router = APIRouter(
    prefix='/publicacao',
    tags=['Publicacao']
)


@router.post("/add_Publicacao", response_model=Publicacao)
def create_pub(pub: Publicacao, session: Session = Depends(get_session)):
    pub.data_criacao= datetime.now(timezone.utc)
    session.add(pub)
    session.commit()
    session.refresh(pub)
    return pub
    

@router.get("/get_Publicacao", response_model=list[Publicacao])
def get_pubs( offset: int = 0, limit: int = Query(default=10, le=50),
             session: Session= Depends(get_session)):
    return session.exec(select(Publicacao).offset(offset).limit(limit)).all()
    

@router.put("/upar_Publicacao", response_model= Publicacao)
def uPpub(pub_id: int, newpub: Publicacao, session: Session= Depends(get_session)):
    
    pub= session.get(Publicacao, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail='pub not found')
    
    for k, v in newpub.dict(exclude_unset=True).items():
        if v is not None and k not in ['id', 'perfil_id']:
            setattr(pub, k, v)
    pub.data_criacao= datetime.now(timezone.utc)
    # session.add(pub)
    session.commit()
    session.refresh(pub)
    return pub


@router.delete('/del_publicacao', response_model=Publicacao)
def delete_pub(pub_id: int, session: Session= Depends(get_session)):
    pub_del= session.get(Publicacao, pub_id)
    if not pub_del:
        raise HTTPException(status_code=404, detail='pub not foun')
    session.delete(pub_del)
    session.commit()
    return pub_del

    