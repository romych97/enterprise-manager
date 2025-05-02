import pytest
from fastapi import status
from models import User
from routers.auth import get_password_hash, verify_password


def test_register_user(client, db_session):
    # Test data
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
    }

    # Make request
    response = client.post("/api/auth/register", json=user_data)

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify user was created in database
    user = db_session.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.full_name == user_data["full_name"]
    assert verify_password(user_data["password"], user.hashed_password)


def test_login_user(client, db_session):
    # Create test user
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
    }
    hashed_password = get_password_hash(user_data["password"])
    user = User(
        email=user_data["email"],
        hashed_password=hashed_password,
        full_name=user_data["full_name"],
    )
    db_session.add(user)
    db_session.commit()

    # Test login
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/auth/token", data=login_data)

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    # Test with invalid credentials
    login_data = {"username": "invalid@example.com", "password": "wrongpassword"}
    response = client.post("/api/auth/token", data=login_data)

    # Assert response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token(client, db_session):
    # Create test user and get refresh token
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
    }
    response = client.post("/api/auth/register", json=user_data)
    refresh_token = response.json()["refresh_token"]

    # Test refresh token
    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
