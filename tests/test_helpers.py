"""Unit tests for helper functions in src.app module."""

import pytest
from src.app import (
    is_valid_email,
    activity_exists,
    is_participant_already_signed_up,
    has_available_capacity,
    activities
)
from copy import deepcopy


@pytest.fixture()
def sample_activities():
    """Provide a sample activities dictionary for testing."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": ["emma@mergington.edu"]
        }
    }


class TestIsValidEmail:
    """Test email validation function."""

    def test_valid_email_with_standard_format(self):
        """Test that a standard email format is valid."""
        assert is_valid_email("student@mergington.edu") is True

    def test_valid_email_with_multiple_dots(self):
        """Test that an email with multiple dots is valid."""
        assert is_valid_email("john.doe@mergington.co.uk") is True

    def test_invalid_email_without_at_symbol(self):
        """Test that an email without @ symbol is invalid."""
        assert is_valid_email("studentmergington.edu") is False

    def test_invalid_email_without_dot_in_domain(self):
        """Test that an email without a dot in domain is invalid."""
        assert is_valid_email("student@mergington") is False

    def test_invalid_email_with_only_at_symbol(self):
        """Test that an email with only @ is invalid."""
        assert is_valid_email("student@") is False

    def test_empty_string_is_invalid(self):
        """Test that an empty string is invalid."""
        assert is_valid_email("") is False


class TestActivityExists:
    """Test activity existence checking function."""

    def test_existing_activity_returns_true(self, sample_activities):
        """Test that an existing activity returns True."""
        assert activity_exists("Chess Club", sample_activities) is True

    def test_another_existing_activity_returns_true(self, sample_activities):
        """Test that another existing activity returns True."""
        assert activity_exists("Programming Class", sample_activities) is True

    def test_nonexistent_activity_returns_false(self, sample_activities):
        """Test that a nonexistent activity returns False."""
        assert activity_exists("Drama Club", sample_activities) is False

    def test_case_sensitive_activity_name(self, sample_activities):
        """Test that activity name matching is case-sensitive."""
        assert activity_exists("chess club", sample_activities) is False

    def test_empty_activities_dict_returns_false(self):
        """Test that checking empty dict returns False."""
        assert activity_exists("Any Club", {}) is False


class TestIsParticipantAlreadySignedUp:
    """Test duplicate signup detection function."""

    def test_already_signed_up_participant_returns_true(self, sample_activities):
        """Test that an already-signed-up participant returns True."""
        assert is_participant_already_signed_up(
            "Chess Club", "michael@mergington.edu", sample_activities
        ) is True

    def test_not_signed_up_participant_returns_false(self, sample_activities):
        """Test that a not-signed-up participant returns False."""
        assert is_participant_already_signed_up(
            "Chess Club", "new.student@mergington.edu", sample_activities
        ) is False

    def test_nonexistent_activity_returns_false(self, sample_activities):
        """Test that a nonexistent activity returns False."""
        assert is_participant_already_signed_up(
            "Drama Club", "michael@mergington.edu", sample_activities
        ) is False

    def test_case_sensitive_email_check(self, sample_activities):
        """Test that email matching is case-sensitive."""
        assert is_participant_already_signed_up(
            "Chess Club", "MICHAEL@MERGINGTON.EDU", sample_activities
        ) is False

    def test_empty_participants_list_returns_false(self, sample_activities):
        """Test that an activity with no participants returns False."""
        sample_activities["Drama Club"] = {
            "description": "Drama activities",
            "schedule": "Mondays",
            "max_participants": 10,
            "participants": []
        }
        assert is_participant_already_signed_up(
            "Drama Club", "student@mergington.edu", sample_activities
        ) is False


class TestHasAvailableCapacity:
    """Test activity capacity checking function."""

    def test_activity_with_available_capacity_returns_true(self, sample_activities):
        """Test that an activity with available capacity returns True."""
        # Programming Class has 1 participant, max 3
        assert has_available_capacity("Programming Class", sample_activities) is True

    def test_activity_at_full_capacity_returns_false(self, sample_activities):
        """Test that a full activity returns False."""
        # Chess Club has 2 participants, max 2
        assert has_available_capacity("Chess Club", sample_activities) is False

    def test_nonexistent_activity_returns_false(self, sample_activities):
        """Test that checking nonexistent activity returns False."""
        assert has_available_capacity("Drama Club", sample_activities) is False

    def test_activity_with_one_slot_available(self, sample_activities):
        """Test activity with only one slot remaining."""
        # Add one more participant to Chess Club (max 2, currently 2 after adding)
        sample_activities["Chess Club"]["max_participants"] = 3
        assert has_available_capacity("Chess Club", sample_activities) is True

    def test_activity_with_many_slots_available(self, sample_activities):
        """Test activity with many slots available."""
        sample_activities["Large Club"] = {
            "description": "Large activity",
            "schedule": "Anytime",
            "max_participants": 100,
            "participants": [f"student{i}@mergington.edu" for i in range(10)]
        }
        assert has_available_capacity("Large Club", sample_activities) is True
