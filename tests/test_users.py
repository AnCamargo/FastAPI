import pytest
from jose import JWTError, jwt
from app import schema
#from .database import client, session #no es necesario gracias al archivo conftest.py
from app.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.token_mins_expire

# def test_root(client):
#     response = client.get("/")
#     #print(response.json())
#     assert response.status_code == 200
#     assert response.json() == {"message": "Hello, this is the root page"}

def test_create_user(client):
    response = client.post(
        "/users/", json={"email": "user_test_1@gmail.com","password": "Password123*"})

    new_user = schema.UserCreateResponse(**response.json())
    assert new_user.email == "user_test_1@gmail.com"
    assert response.status_code == 201

def test_login_user(client, test_user):
    response = client.post(
        "/login", data={"username": test_user['email'],"password": test_user['password']})
    # print(response.json())
    token = schema.Token(**response.json())
    payload = jwt.decode(token.access_token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
    id = payload.get("user_id")
    assert response.status_code == 200
    assert id == test_user['id']
    assert token.access_token.split(" ")[0] == "Bearer"

@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'Password123*', 403), #Invalid email
    ('user_test_1@gmail.com', 'Password123', 403), #Invalid password  
    ('wrongemail@gmail.com', 'Password123', 403), #Invalid email y password
    (None, 'Password123*', 422), #No email
    ('wrongemail@gmail.com', None, 422) #No password
])
def test_incorrect_login(test_user, client, email, password, status_code):
    response = client.post(
        "/login", data={"username": email,"password": password})
    assert response.status_code == status_code
    #assert response.json().get('detail') == detail
