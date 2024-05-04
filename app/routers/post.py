from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schema
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schema.Post])
async def get_posts(db: Session = Depends(get_db)):
    # with connection_pool.getconn() as connection:
    #     with connection.cursor() as  cursor:
    #         cursor.execute("SELECT * FROM posts")
    #         posts = cursor.fetchall()
    #     # Return the connection to the pool
    #     connection_pool.putconn(connection)
    posts = db.query(models.Post).all()
    return posts

@router.get("/latest")
def get_latest_post(db: Session = Depends(get_db), response_model=schema.Post):
    last_post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return last_post

@router.get("/{post_id}")
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
def create_post(post: schema.PostCreate, db: Session = Depends(get_db)):
    #**post.model_dump() entrega algo de esta forma title=post.title, content=post.content, published=post.published con todos los valores de la clase Post de pydantic
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{post_id}", response_model=schema.Post)
def update_post(post_id: int, post: schema.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()