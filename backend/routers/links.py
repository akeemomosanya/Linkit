from typing import Annotated, Optional
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from models import Link
from database import SessionLocal
from .auth import get_current_user
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix='/links',
    tags=['links']
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class LinkCreate(BaseModel):
    url: HttpUrl
    name: Optional[str] = None
    note: Optional[str] = None


class LinkUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    name: Optional[str] = None
    note: Optional[str] = None


class LinkResponse(BaseModel):
    id: int
    url: str
    name: Optional[str]
    note: Optional[str]

    class Config:
        from_attributes = True



@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    db: db_dependency,
    user: user_dependency,
    links_request: LinkCreate,
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    link_model = Link(
        url=str(links_request.url),
        name=links_request.name,
        note=links_request.note,
        owner_id=user['id'],
    )

    try:
        db.add(link_model)
        db.commit()
        db.refresh(link_model)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This URL has already been saved.")

    return link_model


@router.get("/", response_model=list[LinkResponse], status_code=status.HTTP_200_OK)
async def get_links(user: user_dependency, db: db_dependency):
    """Return all links belonging to the current user."""
    return db.query(Link).filter(Link.owner_id == user['id']).all()


@router.get("/search", response_model=list[LinkResponse], status_code=status.HTTP_200_OK)
async def search_links(
    user: user_dependency,
    db: db_dependency,
    name: str,
):
    """Search the current user's links by name (case-insensitive, partial match)."""
    results = (
        db.query(Link)
        .filter(
            Link.owner_id == user['id'],
            Link.name.ilike(f"%{name}%"),
        )
        .all()
    )
    if not results:
        raise HTTPException(status_code=404, detail="No links found matching that name.")
    return results


@router.get("/{link_id}/copy", status_code=status.HTTP_200_OK)
async def copy_link(
    user: user_dependency,
    db: db_dependency,
    link_id: int,
):
    """Return the URL of a link so the user can copy it."""
    link = db.query(Link).filter(Link.id == link_id, Link.owner_id == user['id']).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found.")
    return {"url": link.url}


@router.put("/{link_id}", response_model=LinkResponse, status_code=status.HTTP_200_OK)
async def edit_link(
    user: user_dependency,
    db: db_dependency,
    link_id: int,
    link_update: LinkUpdate,
):
    """Edit any field on an existing link. Only supply the fields you want to change."""
    link = db.query(Link).filter(Link.id == link_id, Link.owner_id == user['id']).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found.")

    if link_update.url is not None:
        link.url = str(link_update.url)
    if link_update.name is not None:
        link.name = link_update.name
    if link_update.note is not None:
        link.note = link_update.note

    try:
        db.commit()
        db.refresh(link)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="That URL is already saved by another link.")

    return link


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    user: user_dependency,
    db: db_dependency,
    link_id: int,
):
    """Permanently delete a link. Returns 204 No Content on success."""
    link = db.query(Link).filter(Link.id == link_id, Link.owner_id == user['id']).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found.")

    db.delete(link)
    db.commit()