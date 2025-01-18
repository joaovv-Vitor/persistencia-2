from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models.perfil import Perfil
from models.publicacao import Publicacao, PubAlbum
from models.album import Album

router = APIRouter(
    prefix='/perfil',  # Prefixo para todas as rotas
    tags=['Perfil'],   # Tag para documentação automática
)


# @router.post('/', response_model=Perfil)  # criar perfil
# def create_perfil(perfil: Perfil, session: Session = Depends(get_session)):
#     session.add(perfil)
#     session.commit()
#     session.refresh(perfil)
#     return perfil


@router.post('/', response_model=Perfil)  # criar perfil
def create_perfil(perfil: Perfil, session: Session = Depends(get_session)):
    # Verifica se já existe um perfil com o mesmo email
    perfilVali = session.exec(select(Perfil).where(Perfil.email == perfil.email)).first()

    if perfilVali:  # Caso o perfil já exista
        raise HTTPException(status_code=400, detail='Email já registrado.')

    # Adiciona o novo perfil
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
        raise HTTPException(status_code=404, detail='Perfil não encontrado.')
    return perfil


@router.put('/{perfil_id}', response_model=Perfil)
def update_perfil(perfil_id: int, perfil_db: Perfil, session: Session = Depends(get_session)):
    perfil = session.get(Perfil, perfil_id)
    if not perfil:
        raise HTTPException(status_code=404, detail='Perfil não encontrado.')

    for field, value in perfil_db.model_dump(exclude_unset=True).items():
        setattr(perfil, field, value)

    session.commit()
    session.refresh(perfil)
    return perfil


@router.delete('/{perfil_id}')
def delete_perfil(perfil_id: int, session: Session = Depends(get_session)):
    perfil = session.get(Perfil, perfil_id)
    if not perfil:
        raise HTTPException(status_code=404, detail='Perfil não encontrado.')
    session.delete(perfil)
    session.commit()
    return {'ok': True}


#quantas publicacoes que um perfil tem

@router.get('/{perfil_id}/publicacoes')
def listar_publicacoes(perfil_id: int, session: Session = Depends(get_session)):
    # Busca todas as publicações relacionadas ao perfil
    query = select(Publicacao).where(Publicacao.perfil_id == perfil_id)
    publicacoes = session.exec(query).all()

    if not publicacoes:
        raise HTTPException(status_code=404, detail='Perfil não encontrado ou perfil não tem publicações.')

    return {"perfil_id": perfil_id, "publicacoes": publicacoes}


# listar todas as publicacoes passando o perfil e o album da publicacao
@router.get('/{perfil_id}/{album_id}/publicacoes')
def listar_publicacoes_do_album(perfil_id: int, album_id: int, session: Session = Depends(get_session)):
    # Consulta com eager loading utilizando SQLModel
    query = (
        select(Publicacao)
        .where(
            Publicacao.perfil_id == perfil_id,
            Publicacao.id.in_(
                select(PubAlbum.pub_id).where(PubAlbum.album_id == album_id)
            )
        )
    )
    publicacoes = session.exec(query).all()

    if not publicacoes:
        raise HTTPException(
            status_code=404,
            detail="Perfil não encontrado ou perfil não tem publicações no álbum especificado."
        )

    return {"perfil_id": perfil_id, "album_id": album_id, "publicacoes": publicacoes}