import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User

# Constants
TEST_EMAIL = "test_rider@example.com"
TEST_PASSWORD = "test123"
AUTH_REGISTER_URL = "/auth/register"
AUTH_LOGIN_URL = "/auth/login"
AUTH_ME_URL = "/auth/me"
POST_LOCATION_URL = "/locations"

@pytest.fixture(scope="function")
def client():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user(client):
    # Create a test user
    response = client.post(AUTH_REGISTER_URL, json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    return response.json()

@pytest.fixture(scope="function")
def auth_token(client, test_user):
    # Get auth token
    response = client.post(AUTH_LOGIN_URL, data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    return response.json()["access_token"]

def test_register_user(client):
    """Test user registration with valid data"""
    response = client.post(AUTH_REGISTER_URL, json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == TEST_EMAIL

def test_register_duplicate_user(client, test_user):
    """Test registration with existing email"""
    response = client.post(AUTH_REGISTER_URL, json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 400
    assert "detail" in response.json()

def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(AUTH_LOGIN_URL, data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(AUTH_LOGIN_URL, data={
        "username": TEST_EMAIL,
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_current_user(client, auth_token):
    """Test getting current user info"""
    response = client.get(AUTH_ME_URL, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["email"] == TEST_EMAIL

def test_get_current_user_no_token(client):
    """Test getting current user without token"""
    response = client.get(AUTH_ME_URL)
    assert response.status_code == 401 


def test_post_location(client, auth_token, test_user):
    """TEst posting location"""
    response = client.post(POST_LOCATION_URL,
                           headers={"Authorization": f"BEARER {auth_token}"},
                           json={"latitude": 48.13, "longitude": 11.57}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "latitude" in data
    assert "longitude" in data
    assert "user_id" in data
    assert data["user_id"] == test_user["id"]

