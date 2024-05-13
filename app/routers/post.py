from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schema, oauth2
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schema.PostResponse])
def get_posts(current_user: dict = Depends(oauth2.get_current_user)
                    , db: Session = Depends(get_db)
                    , limit: int = 10, offset: int = 0, title_search: Optional[str] =""
                    , content_search: Optional[str] = ""):
    # with connection_pool.getconn() as connection:
    #     with connection.cursor() as  cursor:
    #         cursor.execute("SELECT * FROM posts")
    #         posts = cursor.fetchall()
    #     # Return the connection to the pool
    #     connection_pool.putconn(connection)
    #posts = db.query(models.Post).filter(and_(models.Post.user_id == current_user.id, models.Post.title.contains(search))).limit(limit).offset(offset).all()
    
    results = db.query(models.Post, func.count(models.Votes.post_id).label("Votes")).join(
        models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(
                     models.Post.id).filter(
            and_(models.Post.user_id == current_user.id
                 , models.Post.title.contains(title_search)
                 , models.Post.content.contains(content_search))).limit(limit).offset(offset).all()
    return results

@router.get("/latest", response_model=schema.PostResponse)
def get_latest_post(db: Session = Depends(get_db),  current_user: dict = Depends(oauth2.get_current_user)
                    ,response_model=schema.Post):
    results = db.query(models.Post, func.count(models.Votes.post_id).label("Votes")).join(
        models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(
                     models.Post.id).filter(
                         models.Post.user_id == current_user.id).order_by(models.Post.id.desc()).first()
    
    #last_post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return results

@router.get("/{post_id}", response_model=schema.PostResponse)
def get_post_by_id(post_id: int, current_user: dict = Depends(oauth2.get_current_user)
                   , db: Session = Depends(get_db)):
    results = db.query(models.Post, func.count(models.Votes.post_id).label("Votes")).join(
        models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(
                     models.Post.id).filter(models.Post.user_id == current_user.id,
                         models.Post.id == post_id).first()
    #post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    return results

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
def create_post(post: schema.PostCreate, current_user: dict = Depends(oauth2.get_current_user)
                , db: Session = Depends(get_db)):
    #**post.model_dump() entrega algo de esta forma title=post.title, content=post.content, published=post.published con todos los valores de la clase Post de pydantic
    new_post = models.Post(user_id = current_user.id,**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int,  current_user: dict = Depends(oauth2.get_current_user)
                , db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    del_post = post_query.first()
    if del_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    if current_user.id != del_post.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not Authorized to perform requested action.")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{post_id}", response_model=schema.Post)
def update_post(post_id: int, post: schema.PostCreate,  current_user: dict = Depends(oauth2.get_current_user)
                , db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    upd_post = post_query.first()
    if upd_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    if current_user.id != upd_post.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not Authorized to perform requested action.")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()