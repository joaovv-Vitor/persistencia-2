from datetime import datetime, timezone
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from database import get_session
from models.album import Album, AlbumBase
from models.perfil import Perfil, PerfilCompleto
from models.publicacao import PubCompleta, Publicacao, PublicacaoBase

router = APIRouter(
    prefix='/publicacao',
    tags=['Publicacao']
)


# CREATE
@router.post("/", response_model=PubCompleta)
def create_publicacao(pb: Publicacao, session: Session = Depends(get_session)):
    perfil = session.exec(select(Perfil).where(Perfil.id == pb.perfil_id)
                         .options(joinedload(Perfil.publicacoes))).first()
    if not perfil:
        raise HTTPException(status_code=400, detail='perfil invalido')

    pb.data_criacao = datetime.now(timezone.utc)
    session.add(pb)
    session.commit()
    session.refresh(pb)
    return pb


# READ ALL
@router.get("/", response_model=list[Publicacao])
def get_pubs(offset: int = 0, limit: int = Query(default=10, le=50),
             session: Session = Depends(get_session)):
    return session.exec(select(Publicacao).offset(offset).limit(limit)).all()


# RETORNA A PUBLICACAO POR ID
@router.get("/{pub_id}", response_model=PubCompleta)
def read_publicacao(pub_id: int, session: Session = Depends(get_session)):

    statement = (select(Publicacao).where(Publicacao.id == pub_id)
                 .options(joinedload(Publicacao.perfil),
                          joinedload(Publicacao.albuns)))

    post = session.exec(statement).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# ATUALIZA PUBLICACAO
@router.put("/", response_model=Publicacao)
def up_pub(pid: int, pb: Publicacao, session: Session = Depends(get_session)):

    pub = session.get(Publicacao, pid)
    if not pub:
        raise HTTPException(status_code=404, detail='pub not found')

    for k, v in pb.model_dump(exclude_unset=True).items():
        if v is not None and k not in ['id', 'perfil_id']:
            setattr(pub, k, v)
    pub.data_criacao = datetime.now(timezone.utc)
    session.commit()
    session.refresh(pub)
    return pub


# DELETE PUBLICACAO
@router.delete('/', response_model=Publicacao)
def delete_pub(pub_id: int, session: Session = Depends(get_session)):
    pub_del = session.get(Publicacao, pub_id)
    if not pub_del:
        raise HTTPException(status_code=404, detail='pub not foun')
    session.delete(pub_del)
    session.commit()
    return pub_del


# RETORNA O PERFIL DE UMA PUBLICACAO
@router.get("/publicacao{pub_id}/perfil", response_model=PerfilCompleto)
def read_perfil(pub_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Perfil)
        .join(Publicacao, Perfil.id == Publicacao.perfil_id)
        .where(Publicacao.id == pub_id)
    )
    resultado = session.exec(stmt).first()

    if not resultado:
        raise HTTPException(status_code=404, detail="result not found")
    return resultado


# BUSCA POR TEXTO PARCIAL NA LEGENDA
@router.get("/publicacao/parcial", response_model=list[PubCompleta])
def buscar_pub_parcial(
    texto: str = Query(..., description="Texto a ser buscado"),
    offset: int = 0,
    limit: int = Query(default=10, le=50),
    session: Session = Depends(get_session)
):
    stmt = (
        select(Publicacao)
        .where(Publicacao.legenda.like(f"%{texto}%"))  # Busca prcial no txt td
        .offset(offset)
        .limit(limit)
    )
    resultados = session.exec(stmt).all()
    return resultados


# BUSCA PUBLICACOES POR ANO
@router.get("/busca/", response_model=list[Publicacao])
def publicacoes_por_ano_e_perfil(perfil_id: int, ano: int, offset: int = 0,
    limit: int = Query(default=10, le=50),
    session: Session = Depends(get_session)
):
    stmt = (
        select(Publicacao)
        .where(
            (Publicacao.perfil_id == perfil_id) &
            (Publicacao.data_criacao >= datetime(ano, 1, 1,
                                                 tzinfo=timezone.utc)) &
            (Publicacao.data_criacao < datetime(ano + 1, 1, 1,
                                                tzinfo=timezone.utc))
        )
        .offset(offset)
        .limit(limit)
    )

    resultados = session.exec(stmt).all()
    return resultados


# CONTA AS PUBLICACOES TOTAIS
@router.get("/publicacaoes/count", response_model=int)
def contagem_publicacoes(session: Session = Depends(get_session)):
    total = session.exec(select(func.count(Publicacao.id))).one()
    return total


#  PUBLICACOES POR PERFIL
@router.get("/publicacaoes/count/perfil", response_model=int)
def contagem_publicacoes_por_perfil(perfil_id: int,
                                    session: Session = Depends(get_session)):
    perfil = session.get(Perfil, perfil_id)
    if not perfil:
        raise HTTPException(status_code=404, detail='Perfil not found')

    total = session.exec(
        select(func.count(Publicacao.id))
        .where(Publicacao.perfil_id == perfil_id)
    ).one()
    return total


# ORDENA AS PUBLICACOES POR perfil.id
@router.get("/publicacaoes/ordenadas", response_model=list[Publicacao])
def ordena_publicacoes_perfil(session: Session = Depends(get_session)):
    pubs = session.exec(select(Publicacao)
                        .order_by(Publicacao.perfil_id)).all()
    return pubs


# enum para ordenação em curtidas
class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


# PUBLICACOES DE PERFIL ORDENADAS POR LIKES
@router.get("/publicacoes/{perfil_id}/curtidas",
            response_model=list[Publicacao])
def obter_publicacoes_por_likes(
    perfil_id: int,
    order: OrderBy = OrderBy.desc,
    session: Session = Depends(get_session)
):
    order_dict = {
        OrderBy.asc: Publicacao.curtidas.asc(),
        OrderBy.desc: Publicacao.curtidas.desc(),
    }

    stmt = (select(Publicacao).where(Publicacao.perfil_id == perfil_id)
            .order_by(order_dict[order]))
    publicacoes = session.exec(stmt).all()

    if not publicacoes:
        raise HTTPException(status_code=404, detail="Pub not found.")

    return publicacoes


# É USADO PARA FAZER UMA INTERPRETAÇAO POSTERIOR DOS MODELS
# GARANTINDO QUE NÃO VAI DAR ERRO DE INTERPRETAÇÃO ERRADA NA ORDEM
PubCompleta.model_rebuild()
Album.model_rebuild()
PerfilCompleto.model_rebuild()
AlbumBase.model_rebuild()
PublicacaoBase.model_rebuild()
