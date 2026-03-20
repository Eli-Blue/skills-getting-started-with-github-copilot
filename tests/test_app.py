"""
Tests for the Mergington High School API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activity participants to initial state before each test."""
    original_participants = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants in original_participants.items():
        activities[name]["participants"] = participants


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) > 0


def test_get_activities_structure(client):
    response = client.get("/activities")
    assert response.status_code == 200
    activity = response.json()["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity


def test_signup_for_activity_success(client):
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up newstudent@mergington.edu for Chess Club"}
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_activity_not_found(client):
    response = client.post("/activities/Nonexistent Club/signup?email=student@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_already_signed_up(client):
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_success(client):
    response = client.delete("/activities/Chess Club/participants?email=michael@mergington.edu")
    assert response.status_code == 200
    assert response.json() == {"message": "Unregistered michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_participant_activity_not_found(client):
    response = client.delete("/activities/Nonexistent Club/participants?email=student@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_not_in_activity(client):
    response = client.delete("/activities/Chess Club/participants?email=notmember@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
