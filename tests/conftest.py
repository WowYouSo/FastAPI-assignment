import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models import User
from auth import hash_password


# TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db):
    user_data = {"username": "test_user", "password": "test_password"}

    hashed_password = hash_password(user_data["password"])

    db_user = User(username=user_data["username"], hashed_password=hashed_password)
    test_db.add(db_user)
    test_db.commit()
    test_db.refresh(db_user)

    return {"username": user_data["username"], "password": user_data["password"]}


@pytest.fixture(scope="function")
def token(client, test_user):
    response = client.post("/login", data={"username": test_user["username"], "password": test_user["password"]})
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client