from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activity_names = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert expected_activity_names.issubset(payload.keys())
    for activity_name in expected_activity_names:
        assert "participants" in payload[activity_name]
        assert isinstance(payload[activity_name]["participants"], list)


def test_signup_for_activity_adds_participant_and_returns_message(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_for_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Drama Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


# New edge case tests

def test_root_endpoint_redirects_to_static_index(client):
    # Arrange & Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_signup_with_invalid_email_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "invalid-email"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email format"}


def test_signup_with_email_without_dot_returns_400(client):
    # Arrange
    activity_name = "Programming Class"
    email = "student@mergington"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email format"}


def test_signup_with_duplicate_email_returns_409(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 409
    assert response.json() == {"detail": "Already signed up for this activity"}


def test_signup_for_full_activity_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    activities[activity_name]["max_participants"] = 2
    # Chess Club already has 2 participants
    email = "full.tester@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is at maximum capacity"}


def test_signup_when_activity_reaches_capacity_after_previous_signup(client):
    # Arrange
    activity_name = "Gym Class"
    activities[activity_name]["max_participants"] = 3
    # Gym Class has 2 participants, so one slot left
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"

    # Act - First signup should succeed
    response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email1})
    assert response1.status_code == 200

    # Act - Second signup should fail (now at capacity)
    response2 = client.post(f"/activities/{activity_name}/signup", params={"email": email2})

    # Assert
    assert response2.status_code == 400
    assert response2.json() == {"detail": "Activity is at maximum capacity"}


def test_multiple_successful_signups_to_same_activity(client):
    # Arrange
    activity_name = "Programming Class"
    activities[activity_name]["max_participants"] = 25
    emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]

    # Act
    for email in emails:
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response.status_code == 200

    # Assert - Verify all students were added
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    for email in emails:
        assert email in participants


def test_signup_across_different_activities(client):
    # Arrange
    email = "versatile.student@mergington.edu"
    activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
    activities["Chess Club"]["max_participants"] = 15
    activities["Programming Class"]["max_participants"] = 25
    activities["Gym Class"]["max_participants"] = 35

    # Act - Sign up for multiple activities
    for activity_name in activities_to_join:
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response.status_code == 200

    # Assert - Verify student is in all activities
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    for activity_name in activities_to_join:
        assert email in activities_data[activity_name]["participants"]


def test_get_activities_returns_structure_with_required_fields(client):
    # Arrange & Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    for activity_name, activity_data in payload.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)
        assert isinstance(activity_data["max_participants"], int)

