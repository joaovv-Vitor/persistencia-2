from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from  sqlalchemy  import func
from database import get_session
from models.publicacao import Publicacao
from models.perfil import Perfil

router = APIRouter(
    prefix='/publicacao',
    tags=['Publicacao']
)


@router.post("/", response_model=Publicacao)
def create_publicacao(pub: Publicacao, session: Session = Depends(get_session)):
    if pub.perfil_id <= 0:
        raise HTTPException(status_code=400, detail='perfil invalido')
    pub.data_criacao = datetime.now(timezone.utc)
    session.add(pub)
    session.commit()
    session.refresh(pub)
    return pub


@router.get("/", response_model=list[Publicacao])
def get_pubs(offset: int = 0, limit: int = Query(default=10, le=50),
             session: Session = Depends(get_session)):
    return session.exec(select(Publicacao).offset(offset).limit(limit)).all()


@router.get("/{pub_id}", response_model=Publicacao)
def read_pub(pub_id: int, session: Session = Depends(get_session)):
    pub = session.get(Publicacao, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail='pub not found')
    return pub


@router.put("/", response_model=Publicacao)
def up_publicacao(pub_id: int, newpub: Publicacao, session: Session = Depends(get_session)):

    pub = session.get(Publicacao, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail='pub not found')

    for k, v in newpub.model_dump(exclude_unset=True).items():
        if v is not None and k not in ['id', 'perfil_id']:
            setattr(pub, k, v)
    pub.data_criacao = datetime.now(timezone.utc)
    session.commit()
    session.refresh(pub)
    return pub


@router.delete('/', response_model=Publicacao)
def delete_pub(pub_id: int, session: Session = Depends(get_session)):
    pub_del = session.get(Publicacao, pub_id)
    if not pub_del:
        raise HTTPException(status_code=404, detail='pub not foun')
    session.delete(pub_del)
    session.commit()
    return pub_del


@router.get("/publicacao{pub_id}/perfil", response_model=Perfil)
def read_perfil(pub_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Perfil)
        .join(Publicacao, Perfil.id == Publicacao.perfil_id)
        .where(Publicacao.id == pub_id)
    )
    resultado = session.exec(stmt).first()

    if not resultado:
        raise HTTPException(status_code=404, detail="Perfil/publicacao nao encontrado")
    return resultado


@router.get("/publicacao/parcial", response_model=list[Publicacao])
def buscar_pub_parcial(
    texto: str = Query(..., description="Texto a ser buscado"),
    offset: int = 0,
    limit: int = Query(default=10, le=50),
    session: Session = Depends(get_session)
):
    stmt = (
        select(Publicacao)
        .where(Publicacao.legenda.like(f"%{texto}%"))  # Busca parcial
        .offset(offset)
        .limit(limit)
    )
    resultados = session.exec(stmt).all()
    return resultados


@router.get("/busca/", response_model=list[Publicacao])
def publicacoes_por_ano(ano: int, session: Session = Depends(get_session)):
    resultado = session.exec(
        select(Publicacao).where(Publicacao.data_criacao >= datetime(ano, 1, 1, tzinfo=timezone.utc))
        .where(Publicacao.data_criacao < datetime(ano + 1, 1, 1, tzinfo=timezone.utc))
    ).all()
    return resultado


@router.get("/publicacaoes/count", response_model=int)
def contagem_publicacoes(session: Session = Depends(get_session)):
    total = session.exec(select(func.count(Publicacao.id))).one()
    return total


@router.get("/publicacaoes/ordenadas", response_model=list[Publicacao])
def ordena_publicacoes(session: Session = Depends(get_session)):
    pubs = session.exec(select(Publicacao).order_by(Publicacao.perfil_id)).all()
    return pubs



