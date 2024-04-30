from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

n_tries_conn = 0
while True:
    if n_tries_conn == 5:
        print('5 failed tries to connect to the Database.')
        raise Exception('error trying to connect to the database')
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(1,
                                                             10,
                                                             host = 'localhost',
                                                             database = 'fastapi',
                                                             user = 'postgres',
                                                             password = 'Soratoshiro95*',
                                                             cursor_factory=RealDictCursor)
        #cursor = conn.cursor()
        print("Database connection was succesfull!!")
        break
    except Exception as error: 
        print("Connection to the Database failed.")
        print(error)
        n_tries_conn += 1
        time.sleep(2)

my_posts = [{"id": 1,"title": "Post 1", "content": "Content 1"},
            {"id": 2,"title": "Post 2", "content": "Content 2"},
            {"id": 3,"title": "Post 3", "content": "Content 3"}]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
        
def find_index(id):
    for index, p in enumerate(my_posts):
        if p["id"] == id:
            return index

@app.get("/")
def root():
    return {"message": "Hello this is the root page"}

@app.get("/posts")
async def get_posts():
    with connection_pool.getconn() as connection:
        with connection.cursor() as  cursor:
            cursor.execute("SELECT * FROM posts")
            posts = cursor.fetchall()
        # Return the connection to the pool
        connection_pool.putconn(connection)
    return {"data": posts}

@app.get("/posts/latest")
def get_latest_post():
    return {"last_post": my_posts[-1]}

@app.get("/posts/{post_id}")
def get_post_by_id(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    return {"post_detail": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post_dict = post.model_dump()
    id = len(my_posts) + 1
    post_dict["id"] = id
    my_posts.append(post_dict)
    print(post_dict)
    return {"data": post_dict}

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    index = find_index(post_id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
    index = find_index(post_id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not exist")
    post_dict = post.model_dump()
    post_dict['id'] = post_id
    my_posts[index] = post_dict
    return {"data": post_dict}