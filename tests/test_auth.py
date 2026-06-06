from fastapi.testclient import TestClient
from tests.utils import client, TestingSessionLocal
from backend.models import Users
from backend.database import Base



def test_create_user_success():
    response = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "StrongP@ss1"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "testuser@example.com"


def test_create_user_email_conflict():
    response = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "first_name": "Duplicate",
            "last_name": "User",
            "password": "AnotherP@ss2"
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email is already registered."}


def test_create_user_invalid_email():
    response = client.post(
        "/auth/register",
        json={
            "email": "invalid-email",
            "first_name": "Invalid",
            "last_name": "Email",
            "password": "ValidP@ss1"
        }
    )
    assert response.status_code == 422  


def test_create_user_weak_password():
    response = client.post(
        "/auth/register",
        json={
            "email": "weakpassword@example.com",
            "first_name": "Weak",
            "last_name": "Password",
            "password": "1234567"
        }
    )
    assert response.status_code == 422  


def test_create_user_missing_fields():
    response = client.post(
        "/auth/register",
        json={
            "email": "missingfields@example.com",
            "first_name": "Missing"
        }
    )
    assert response.status_code == 422  



def test_database_interaction():
    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.email == "testuser@example.com").first()
    assert user is not None
    assert user.email == "testuser@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.hashed_password is not None  
    db.close()
