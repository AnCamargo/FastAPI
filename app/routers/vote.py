from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schema, oauth2
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..database import get_db

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)

@router.post("/", status_code=status.HTTP_200_OK)
def vote_post(vote_data: schema.VoteReq, current_user: dict = Depends(oauth2.get_current_user)
                    , db: Session = Depends(get_db)):
    #Revisar que el post existe
    post = db.query(models.Post).filter(models.Post.id == vote_data.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {vote_data.post_id} does not exist")
    #Revisar que no existe la combinacion post_id y user_id
    vote_query = db.query(models.Votes).filter(and_(models.Votes.post_id == vote_data.post_id,models.Votes.user_id == current_user.id))
    vote_post = vote_query.first()
    if vote_post and vote_data.vote_dir == 0:
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"content":f"Vote for the user email {current_user.email} and post with id {vote_data.post_id} have been deleted"}
    elif not vote_post and vote_data.vote_dir == 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Vote for the user email {current_user.email} and post with id {vote_data.post_id} doesn't exist and vote_dir = 0.")
    like = True if vote_data.vote_dir == 1 else False
    if vote_post:
        vote_query.update({models.Votes.user_id: current_user.id
                           , models.Votes.post_id: vote_data.post_id
                           , models.Votes.is_like:  like}, synchronize_session=False)
        db.commit()
        return vote_query.first()
    new_vote = models.Votes(user_id = current_user.id, post_id = vote_data.post_id, is_like = like)
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    return new_vote