"""Unit tests for helper functions in the src.app module."""

import pytest

from src.app import (
    activity_exists,
    has_available_capacity,
    is_participant_already_signed_up,
    is_valid_email,
)


@pytest.fixture()
def sample_activities():
    """Provide an isolated activity collection for helper tests."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": ["emma@mergington.edu"],
        },
    }


class TestIsValidEmail:
    @pytest.mark.parametrize(
        ("email", "expected"),
        [
            ("student@mergington.edu", True),
            ("john.doe@mergington.co.uk", True),
            ("studentmergington.edu", False),
            ("student@mergington", False),
            ("student@", False),
            ("", False),
        ],
    )
    def test_email_validation(self, email, expected):
        # Arrange
        candidate_email = email

        # Act
        result = is_valid_email(candidate_email)

        # Assert
        assert result is expected


class TestActivityExists:
    @pytest.mark.parametrize(
        ("activity_name", "activities", "expected"),
        [
            (
                "Chess Club",
                {
                    "Chess Club": {
                        "max_participants": 2,
                        "participants": [],
                    }
                },
                True,
            ),
            (
                "Programming Class",
                {
                    "Programming Class": {
                        "max_participants": 3,
                        "participants": [],
                    }
                },
                True,
            ),
            ("Drama Club", {}, False),
            ("chess club", {"Chess Club": {}}, False),
            ("Any Club", {}, False),
        ],
    )
    def test_activity_existence(self, activity_name, activities, expected):
        # Arrange
        requested_activity = activity_name

        # Act
        result = activity_exists(requested_activity, activities)

        # Assert
        assert result is expected


class TestIsParticipantAlreadySignedUp:
    @pytest.mark.parametrize(
        ("activity_name", "email", "expected"),
        [
            ("Chess Club", "michael@mergington.edu", True),
            ("Chess Club", "new.student@mergington.edu", False),
            ("Drama Club", "michael@mergington.edu", False),
            ("Chess Club", "MICHAEL@MERGINGTON.EDU", False),
        ],
    )
    def test_participant_signup_status(
        self, sample_activities, activity_name, email, expected
    ):
        # Arrange
        requested_activity = activity_name
        participant_email = email

        # Act
        result = is_participant_already_signed_up(
            requested_activity, participant_email, sample_activities
        )

        # Assert
        assert result is expected

    def test_empty_participants_list_returns_false(self, sample_activities):
        # Arrange
        sample_activities["Drama Club"] = {
            "description": "Drama activities",
            "schedule": "Mondays",
            "max_participants": 10,
            "participants": [],
        }

        # Act
        result = is_participant_already_signed_up(
            "Drama Club", "student@mergington.edu", sample_activities
        )

        # Assert
        assert result is False


class TestHasAvailableCapacity:
    def test_activity_with_available_capacity_returns_true(self, sample_activities):
        # Arrange
        activity_name = "Programming Class"

        # Act
        result = has_available_capacity(activity_name, sample_activities)

        # Assert
        assert result is True

    @pytest.mark.parametrize("activity_name", ["Chess Club", "Drama Club"])
    def test_activity_without_available_capacity_returns_false(
        self, sample_activities, activity_name
    ):
        # Arrange
        requested_activity = activity_name

        # Act
        result = has_available_capacity(requested_activity, sample_activities)

        # Assert
        assert result is False

    def test_activity_with_one_slot_available_returns_true(self, sample_activities):
        # Arrange
        sample_activities["Chess Club"]["max_participants"] = 3

        # Act
        result = has_available_capacity("Chess Club", sample_activities)

        # Assert
        assert result is True

    def test_activity_with_many_slots_available_returns_true(self, sample_activities):
        # Arrange
        sample_activities["Large Club"] = {
            "description": "Large activity",
            "schedule": "Anytime",
            "max_participants": 100,
            "participants": [f"student{i}@mergington.edu" for i in range(10)],
        }

        # Act
        result = has_available_capacity("Large Club", sample_activities)

        # Assert
        assert result is True
