def test_vote_on_post(authorized_client, test_posts):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[0].id, "vote_dir": 1})
    assert response.status_code == 200

    