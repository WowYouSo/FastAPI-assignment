import pytest
from fastapi import status
from jose import jwt
from auth import SECRET_KEY, ALGORITHM

def test_create_user(client):
    user_data = {"username": "new_user", "password": "new_password"}
    response = client.post("/register", json=user_data)

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == user_data["username"]
    assert "id" in data
    
    assert "password" not in data
    assert "hashed_password" not in data

def test_create_user_duplicate_username(client, test_user):
    response = client.post("/register", json={"username": test_user["username"], "password": "password123"})

    assert response.status_code == 400
    
    assert response.json()["detail"] == "Username already registered"

def test_login_user(client, test_user):
    response = client.post("/login", data={"username": test_user["username"], "password": test_user["password"]})
    
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == test_user["username"]


def test_login_incorrect_password(client, test_user):
    response = client.post("/login", data={"username": test_user["username"], "password": "wrong_password"})
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_nonexistent_user(client):
    response = client.post("/login", data={"username": "non_existent_user", "password": "password123"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"