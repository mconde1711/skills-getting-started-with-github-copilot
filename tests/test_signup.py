"""Test cases for activity signup functionality"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


def test_successful_signup(client):
    """Test that a new student can successfully sign up for an activity"""
    response = client.post("/activities/Chess%20Club/signup?email=alice@mergington.edu")
    assert response.status_code == 200
    assert "alice@mergington.edu" in activities["Chess Club"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == 3


def test_duplicate_signup_rejected(client):
    """Test that a student cannot sign up twice for the same activity"""
    # First signup should succeed
    response1 = client.post("/activities/Chess%20Club/signup?email=alice@mergington.edu")
    assert response1.status_code == 200
    assert len(activities["Chess Club"]["participants"]) == 3

    # Second signup with the same email should fail
    response2 = client.post("/activities/Chess%20Club/signup?email=alice@mergington.edu")
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"]
    # Participant list should not have duplicate entries
    assert len(activities["Chess Club"]["participants"]) == 3


def test_already_registered_student_cannot_register_again(client):
    """Test that existing participants cannot register again"""
    # michael@mergington.edu is already in Chess Club
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_nonexistent_activity_returns_404(client):
    """Test that signing up for a non-existent activity returns 404"""
    response = client.post("/activities/Nonexistent%20Activity/signup?email=alice@mergington.edu")
    assert response.status_code == 404


def test_multiple_different_students_can_signup(client):
    """Test that multiple different students can sign up for the same activity"""
    response1 = client.post("/activities/Chess%20Club/signup?email=alice@mergington.edu")
    response2 = client.post("/activities/Chess%20Club/signup?email=bob@mergington.edu")
    response3 = client.post("/activities/Chess%20Club/signup?email=charlie@mergington.edu")

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
    assert len(activities["Chess Club"]["participants"]) == 5
    assert activities["Chess Club"]["participants"].count("alice@mergington.edu") == 1
    assert activities["Chess Club"]["participants"].count("bob@mergington.edu") == 1
    assert activities["Chess Club"]["participants"].count("charlie@mergington.edu") == 1
