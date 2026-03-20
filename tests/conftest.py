from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture()
def client():
    original_activities = deepcopy(activities)
    try:
        yield TestClient(app)
    finally:
        activities.clear()
        activities.update(deepcopy(original_activities))
