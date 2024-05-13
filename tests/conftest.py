from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db
from app.database import Base
import pytest
from alembic import command
from app.oauth2 import create_access_token
from app import models

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_pw}@{settings.db_host}:{settings.db_port}/{settings.db_name}_test"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    #run our code before we run our test
    #command.upgrade("head")
    yield TestClient(app)
    # run our code after our test finishes

@pytest.fixture
def test_user(client):
    user_data = {"email": "user_test_1@gmail.com",
                 "password": "Password123*"}
    res = client.post("/users/", json = user_data)
    new_user = res.json()
    new_user['password'] = user_data['password']
    assert res.status_code == 201
    return new_user

@pytest.fixture
def test_user2(client):
    user_data = {"email": "user_test_2@gmail.com",
                 "password": "Password123*"}
    res = client.post("/users/", json = user_data)
    new_user = res.json()
    new_user['password'] = user_data['password']
    assert res.status_code == 201
    return new_user

@pytest.fixture
def token(test_user):
    return 'Bearer ' +  create_access_token(data={"user_id":test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": token
    }
    return client

@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [{
        "title": "1st title",
        "content": "1st content",
        "user_id": test_user['id']
        },
        {
        "title": "2nd title",
        "content": "2nd content",
        "user_id": test_user['id'] 
        },
        {
        "title": "3rd title",
        "content": "3rd content",
        "user_id": test_user['id'] 
        },
        {
        "title": "4th title",
        "content": "4th content",
        "user_id": test_user2['id'] 
        }]
    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)

    session.add_all(posts)
    session.commit()

    posts = session.query(models.Post).all()
    return posts    