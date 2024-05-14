import pytest
from app import models, schema


@pytest.fixture()
def test_vote(test_posts, session, test_user):
    new_vote = models.Votes(post_id=test_posts[2].id, user_id = test_user['id'], is_like = False)
    session.add(new_vote)
    session.commit()

def test_vote_on_post(authorized_client, test_posts):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[0].id, "vote_dir": 1})
    assert response.status_code == 200

def test_vote_on_post_already_voted(authorized_client, test_posts, test_vote):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[2].id, "vote_dir": 1})
    assert response.status_code == 200
    assert response.json()['is_like'] == True

def test_delete_vote(authorized_client, test_posts, test_vote, test_user):
    id_post = test_posts[2].id
    response = authorized_client.post("/vote/", json={"post_id": test_posts[2].id, "vote_dir": 0})
    assert response.status_code == 200
    assert response.json()['content'] == f"Vote for the user email {test_user['email']} and post with id {id_post} have been deleted"

def test_delete_vote_non_exist_dir_0(authorized_client, test_posts, test_user):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[2].id, "vote_dir": 0})
    assert response.status_code == 406

def test_delete_vote_non_exist_dir_diff_0(authorized_client, test_user):
    response = authorized_client.post("/vote/", json={"post_id": 555, "vote_dir": 1})
    assert response.status_code == 404

def test_vote_unauthorized_user(client, test_posts):
    response = client.post("/vote/", json={"post_id": test_posts[0].id, "vote_dir": 1})
    assert response.status_code == 401