from fastapi.testclient import TestClient
import app
import pytest

@pytest.fixture(autouse=True)
def monkeypatch_db(monkeypatch: pytest.MonkeyPatch):
    from sqlalchemy import create_engine, StaticPool
    from sqlalchemy.orm import sessionmaker
    from models import Base

    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)  # Create tables
    db = sessionmaker(bind=engine)

    # Monkeypatch the db variable in the app module
    monkeypatch.setattr(app, "db", db)

client = TestClient(app.app)

def test_create_completion_habit():
    response = client.post("/habits/new", json={
        "name": "Test Completion Habit",
        "type": "completion",
        "completion_target": 1,
        "target_timeframe": "day"
    })
    # print(response.json())
    assert response.status_code == 201

    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()
    assert len(habits) == 1
    assert habits[0]["name"] == "Test Completion Habit"
    assert habits[0]["habit_type"] == "completion"
    assert habits[0]["completion_target"] == 1
    assert habits[0]["target_timeframe"] == "day"

def test_log_completion_habit():
    # First, create a habit to log against
    response = client.post("/habits/new", json={
        "name": "Test Completion Habit",
        "type": "completion",
        "completion_target": 1,
        "target_timeframe": "day"
    })
    assert response.status_code == 201

    # Get the habit ID
    response = client.get("/habits")
    habit_id = response.json()[0]["id"]

    # Log a completion for the habit
    response = client.post(f"/log/{habit_id}", json={
        "log_date": "2024-01-01T00:00:00Z",
        "status": True,
        "type": "completion"
    })
    assert response.status_code == 200

    # Verify that the log entry was created
    response = client.get(f"/log/{habit_id}")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["status"] == True
    assert logs[0]["habit_type"] == "completion"

def test_log_choice_habit():
    # Create a choice habit
    response = client.post("/habits/new", json={
        "name": "Test Choice Habit",
        "type": "choice",
        "options": [
            {
                "option_text": "Option 1",
                "color": "red",
                "icon": "icon1"
            },
            {
                "option_text": "Option 2", # Test that options may not have color or icon
            }
        ]
    })
    assert response.status_code == 201

    # Get the habit ID and option ID
    response = client.get("/habits")
    habit_id = response.json()[0]["id"]
    option_id = response.json()[0]["options"][0]["id"]

    # Log a choice for the habit
    response = client.post(f"/log/{habit_id}", json={
        "log_date": "2024-01-01T00:00:00Z",
        "option_id": option_id,
        "type": "choice"
    })
    assert response.status_code == 200

    # Verify that the log entry was created
    response = client.get(f"/log/{habit_id}")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["option"]["id"] == option_id
    assert logs[0]["habit_type"] == "choice"