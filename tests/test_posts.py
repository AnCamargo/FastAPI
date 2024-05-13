import pytest
from typing import List
from app import schema

def test_get_all_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts")
    def validate(post):
        return schema.PostResponse(**post)
    
    posts_map = map(validate, response.json())
    #posts = schema.PostResponse(List[response.json()])
    posts_list = list(posts_map)
    #Filtra los posts que tienen el mismo user.
    test_posts = [x for x in test_posts if x.user_id == posts_list[0].Post.user_id]
    #print(list(posts_map))
    assert posts_list[0].Post.id == test_posts[0].id
    assert len(response.json()) == len(test_posts)
    assert response.status_code == 200

def test_unauthorized_user_get_all_posts(client, test_posts):
    response = client.get("/posts")
    assert response.status_code == 401

def test_unauthorized_user_get_one_post(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_get_one_post(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/{test_posts[0].id}")
    #print(response.json())
    post = schema.PostResponse(**response.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title
    assert response.status_code == 200

def test_get_one_post_not_exist(authorized_client, test_posts):
    response = authorized_client.get("/posts/4")
    assert response.status_code == 404

@pytest.mark.parametrize("title, content, published", [
    ("1 new title", "1 new content", True),
    ("2 new title", "2 new content", False),
    ("3 new title", "3 new content", True)
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    response = authorized_client.post("/posts/", json={
        "title": title, "content": content, "published": published})

    created_post = schema.Post(**response.json())
    assert response.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.user_id == test_user['id']

@pytest.mark.parametrize("title, content", [
    ("1 new title", "1 new content")
])
def test_create_post_default_published_true(authorized_client, test_user, test_posts, title, content, ):
    response = authorized_client.post("/posts/", json={
        "title": title, "content": content})
    created_post = schema.Post(**response.json())
    assert response.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == True
    assert created_post.user_id == test_user['id']

def test_unauthorized_user_get_create_posts(client, test_user, test_posts):
    response = client.post("/posts/", json={
        "title": "title", "content": "content"})
    assert response.status_code == 401

def test_unauthorized_delete_post(client, test_user, test_posts):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_delete_succesful_post(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 204

def test_delete_post_no_exist(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/555")
    assert response.status_code == 404

def test_delete_other_user_post(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert response.status_code == 403

def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id
    }
    response = authorized_client.put(f"/posts/{test_posts[0].id}", json = data)
    updated_post = schema.Post(**response.json())
    assert response.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']

def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[3].id
    }
    response = authorized_client.put(f"/posts/{test_posts[3].id}", json = data)
    assert response.status_code == 403

def test_unauthorized_update_post(client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id
    }
    response = client.put(f"/posts/{test_posts[0].id}", json = data)
    assert response.status_code == 401

def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id
    }
    response = authorized_client.put(f"/posts/555", json = data)
    assert response.status_code == 404