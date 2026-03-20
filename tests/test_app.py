import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities database before each test."""
    initial_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_for_activity_success():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_for_activity_already_signed_up():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_activity_not_found():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.post("/activities/NonexistentClub/signup", params={"email": "foo@bar.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_full():
    # Arrange
    client = TestClient(app)
    activity = "Gym Class"
    activities[activity]["participants"] = [f"u{i}@mergington.edu" for i in range(activities[activity]["max_participants"])]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": "extra@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_remove_participant_success():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": "missing@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_activity_not_found():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.delete("/activities/NoClub/participants", params={"email": "foo@bar.com"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_root_redirects_to_static_index():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
