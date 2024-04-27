from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

my_posts = [{"id": 1,"title": "Post 1", "content": "Content 1"},
            {"id": 2,"title": "Post 2", "content": "Content 2"},
            {"id": 3,"title": "Post 3", "content": "Content 3"}]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

@app.get("/")
def root():
    return {"message": "Hello this is the root page"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.get("/posts/latest")
def get_latest_post():
    return {"last_post": my_posts[-1]}

@app.get("/posts/{post_id}")
def get_post_by_id(post_id: int, response: Response):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} not found")
    return {"post_detail": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post_dict = post.model_dump()
    id = len(my_posts) + 1
    post_dict["id"] = id
    my_posts.append(post_dict)
    print(post_dict)
    return {"data": post_dict}
