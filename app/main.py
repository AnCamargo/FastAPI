from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from typing import List

# import psycopg2
# from psycopg2 import pool
# from psycopg2.extras import RealDictCursor
# import time

from sqlalchemy.orm import Session

from . import models, schema
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# n_tries_conn = 0
# while True:
#     if n_tries_conn == 5:
#         print('5 failed tries to connect to the Database.')
#         raise Exception('error trying to connect to the database')
#     try:
#         connection_pool = psycopg2.pool.SimpleConnectionPool(1,
#                                                              10,
#                                                              host = 'localhost',
#                                                              database = 'fastapi',
#                                                              user = 'postgres',
#                                                              password = 'Soratoshiro95*',
#                                                              cursor_factory=RealDictCursor)
#         #cursor = conn.cursor()
#         print("Database connection was succesfull!!")
#         break
#     except Exception as error: 
#         print("Connection to the Database failed.")
#         print(error)
#         n_tries_conn += 1
#         time.sleep(2)

@app.get("/")
def root():
    return {"message": "Hello this is the root page"}

@app.get("/posts", response_model=List[schema.Post])
async def get_posts(db: Session = Depends(get_db)):
    # with connection_pool.getconn() as connection:
    #     with connection.cursor() as  cursor:
    #         cursor.execute("SELECT * FROM posts")
    #         posts = cursor.fetchall()
    #     # Return the connection to the pool
    #     connection_pool.putconn(connection)
    posts = db.query(models.Post).all()
    return posts

@app.get("/posts/latest")
def get_latest_post(db: Session = Depends(get_db), response_model=schema.Post):
    # with connection_pool.getconn() as connection:
    #     with connection.cursor() as  cursor:
    #         cursor.execute("SELECT * FROM posts ORDER BY ID DESC LIMIT 1")
    #         last_post = cursor.fetchone()
    #     connection_pool.putconn(connection)
    last_post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return last_post

@app.get("/posts/{post_id}")
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    # with connection_pool.getconn() as connection:
    #     with connection.cursor() as  cursor:
    #         cursor.execute("SELECT * FROM posts WHERE id = %s",(post_id,))
    #         post = cursor.fetchone()
    #     connection_pool.putconn(connection)
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    return post

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
def create_post(post: schema.PostCreate, db: Session = Depends(get_db)):
    # with connection_pool.getconn() as connection:
    #     with connection.cursor() as  cursor:
    #         cursor.execute("INSERT INTO posts (title,content, published, rating) VALUES (%s,%s,%s,%s) RETURNING *", (post.title, post.content, post.published, post.rating))
    #         new_post = cursor.fetchone()
    #     connection.commit()
    #     connection_pool.putconn(connection)
    #**post.model_dump() entrega algo de esta forma title=post.title, content=post.content, published=post.published con todos los valores de la clase Post de pydantic
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    # with connection_pool.getconn() as connection:
    #     with connection.cursor() as  cursor:
    #         cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (post_id,))
    #         post_deleted = cursor.fetchone()
    #     connection.commit()
    #     connection_pool.putconn(connection)
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{post_id}", response_model=schema.Post)
def update_post(post_id: int, post: schema.PostCreate, db: Session = Depends(get_db)):
    # with connection_pool.getconn() as connection:
    #     with connection.cursor() as  cursor:
    #         cursor.execute("UPDATE posts SET title = %s, content =%s, published = %s,  rating = %s WHERE id = %s RETURNING *", (post.title, post.content, post.published, post.rating,post_id,))
    #         post_updated = cursor.fetchone()
    #     connection.commit()
    #     connection_pool.putconn(connection)
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()