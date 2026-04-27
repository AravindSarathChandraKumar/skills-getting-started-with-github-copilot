import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial activities data for resetting
INITIAL_ACTIVITIES = {
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
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act in plays and learn theater skills",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["mason@mergington.edu", "charlotte@mergington.edu"]
    },
    "Debate Club": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["ethan@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Tuesdays, 3:00 PM - 4:30 PM",
        "max_participants": 25,
        "participants": ["harper@mergington.edu", "logan@mergington.edu"]
    }
}


@pytest.fixture
def client():
    # Arrange: Reset activities to initial state
    activities.clear()
    activities.update(INITIAL_ACTIVITIES)
    yield TestClient(app, follow_redirects=False)


def test_root_redirect(client):
    # Arrange: TestClient is set up with app
    # Act: Send GET request to root
    response = client.get("/")
    # Assert: Check redirect to static file
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    # Arrange: Activities are loaded
    # Act: Fetch all activities
    response = client.get("/activities")
    # Assert: Returns full activities data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Number of activities
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_success(client):
    # Arrange: Valid activity and new email
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act: Signup for activity
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert: Success and email added
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in activities[activity]["participants"]


def test_signup_activity_not_found(client):
    # Arrange: Invalid activity name
    activity = "Invalid Activity"
    email = "test@edu"
    # Act: Attempt signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert: 404 error
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_duplicate(client):
    # Arrange: Email already signed up
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in initial data
    # Act: Attempt duplicate signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert: 400 error
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_beyond_max_participants(client):
    # Arrange: Signup until beyond max (currently allowed)
    activity = "Basketball Team"  # max 15, has 1
    email = "extra@student.edu"
    # Act: Signup additional
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert: Succeeds (no enforcement)
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_delete_success(client):
    # Arrange: Email is signed up
    activity = "Chess Club"
    email = "michael@mergington.edu"
    # Act: Delete participant
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert: Success and email removed
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email not in activities[activity]["participants"]


def test_delete_activity_not_found(client):
    # Arrange: Invalid activity
    activity = "Invalid"
    email = "test@edu"
    # Act: Attempt delete
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert: 404 error
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_delete_not_signed_up(client):
    # Arrange: Valid activity, email not signed up
    activity = "Chess Club"
    email = "notsigned@edu"
    # Act: Attempt delete
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert: 404 error
    assert response.status_code == 404
    data = response.json()
    assert "not signed up" in data["detail"]


def test_delete_from_empty_activity(client):
    # Arrange: Activity with no participants (modify data)
    activity = "Art Club"
    activities[activity]["participants"] = []  # Clear participants
    email = "fake@edu"
    # Act: Attempt delete
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert: 404 error
    assert response.status_code == 404
    data = response.json()
    assert "not signed up" in data["detail"]