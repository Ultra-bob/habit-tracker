from fastapi.testclient import TestClient
import app
import pytest


@pytest.fixture(autouse=True)
def monkeypatch_db(monkeypatch: pytest.MonkeyPatch):
    from sqlalchemy import create_engine, StaticPool
    from sqlalchemy.orm import sessionmaker
    from db_models import Base

    # Create an in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)  # Create tables
    db = sessionmaker(bind=engine)

    # Monkeypatch the db variable in the app module
    monkeypatch.setattr(app, "db", db)


client = TestClient(app.app)


def test_create_completion_habit():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Completion Habit",
            "type": "completion",
            "completion_target": 1,
            "target_timeframe": "day",
        },
    )
    assert response.status_code == 201

    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()
    assert len(habits) == 1
    assert habits[0]["name"] == "Test Completion Habit"
    assert habits[0]["habit_type"] == "completion"
    assert habits[0]["completion_target"] == 1
    assert habits[0]["target_timeframe"] == "day"


def test_create_choice_habit():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Choice Habit",
            "type": "choice",
            "options": [
                {"option_text": "Option 1", "color": "red", "icon": "icon1"},
                {
                    "option_text": "Option 2",  # Test that options may not have color or icon
                },
            ],
        },
    )
    assert response.status_code == 201

    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()
    assert len(habits) == 1
    assert habits[0]["name"] == "Test Choice Habit"
    assert habits[0]["habit_type"] == "choice"
    assert len(habits[0]["options"]) == 2
    assert habits[0]["options"][0]["option_text"] == "Option 1"
    assert habits[0]["options"][0]["color"] == "red"
    assert habits[0]["options"][0]["icon"] == "icon1"
    assert habits[0]["options"][1]["option_text"] == "Option 2"
    assert habits[0]["options"][1].get("color") is None
    assert habits[0]["options"][1].get("icon") is None


def test_modify_habit():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Completion Habit",
            "type": "completion",
            "completion_target": 1,
            "target_timeframe": "day",
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.patch(
        f"/habits/{habit_id}",
        json={
            "name": "Updated Completion Habit",
            "completion_target": 2,
            "type": "completion",
        },
    )
    assert response.status_code == 200

    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()
    assert len(habits) == 1
    assert habits[0]["name"] == "Updated Completion Habit"
    assert habits[0]["completion_target"] == 2
    assert habits[0]["habit_type"] == "completion"

def test_add_habit_option():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Choice Habit",
            "type": "choice",
            "options": [
                {"option_text": "Option 1", "icon": "icon1"},
            ],
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.post(
        f"/habits/{habit_id}/options",
        json={"option_text": "Option 2", "color": "blue"},
    )
    assert response.status_code == 200

    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()
    assert len(habits) == 1
    assert len(habits[0]["options"]) == 2
    assert habits[0]["options"][1]["option_text"] == "Option 2"
    assert habits[0]["options"][1]["color"] == "blue"

def test_modify_habit_option():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Choice Habit",
            "type": "choice",
            "options": [
                {"option_text": "Option 1", "icon": "icon1"},
            ],
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.get("/habits")
    option_id = response.json()[0]["options"][0]["id"]

    response = client.patch(
        f"/habits/{habit_id}/options/{option_id}",
        json={"option_text": "Updated Option 1", "color": "green"},
    )
    assert response.status_code == 200

    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()
    assert len(habits) == 1
    assert len(habits[0]["options"]) == 1
    assert habits[0]["options"][0]["option_text"] == "Updated Option 1"
    assert habits[0]["options"][0]["color"] == "green"

def test_reject_option_addition_for_non_choice_habit():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Completion Habit",
            "type": "completion",
            "completion_target": 1,
            "target_timeframe": "day",
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.post(
        f"/habits/{habit_id}/options",
        json={"option_text": "Option 1", "color": "red"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Habit is not a choice habit"

def test_reject_mismatched_log_type():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Completion Habit",
            "type": "completion",
            "completion_target": 1,
            "target_timeframe": "day",
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.post(
        f"/log/{habit_id}",
        json={
            "log_date": "2024-01-01T00:00:00Z",
            "option_id": 1,
            "type": "choice",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Habit type mismatch"


def test_reject_invalid_option_log():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Choice Habit",
            "type": "choice",
            "options": [
                {"option_text": "Option 1", "color": "red", "icon": "icon1"},
            ],
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.post(
        f"/log/{habit_id}",
        json={
            "log_date": "2024-01-01T00:00:00Z",
            "option_id": 999,
            "type": "choice",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Option not found"


def test_reject_option_log_for_wrong_habit():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Choice Habit 1",
            "type": "choice",
            "options": [
                {"option_text": "Option 1", "color": "red", "icon": "icon1"},
            ],
        },
    )
    assert response.status_code == 201
    habit_id_1 = response.json()["id"]

    response = client.post(
        "/habits/new",
        json={
            "name": "Test Choice Habit 2",
            "type": "choice",
            "options": [
                {"option_text": "Option 2", "color": "blue", "icon": "icon2"},
            ],
        },
    )
    assert response.status_code == 201
    habit_id_2 = response.json()["id"]

    assert habit_id_1 != habit_id_2 # No clue when this would not pass, but just to be safe

    response = client.get("/habits")
    habits = response.json()
    option_id_1 = habits[0]["options"][0]["id"]

    response = client.post(
        f"/log/{habit_id_2}",
        json={
            "log_date": "2024-01-01T00:00:00Z",
            "option_id": option_id_1,
            "type": "choice",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Option does not belong to the specified habit"


def test_log_completion_habit():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Completion Habit",
            "type": "completion",
            "completion_target": 1,
            "target_timeframe": "day",
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.post(
        f"/log/{habit_id}",
        json={"log_date": "2024-01-01T00:00:00Z", "status": True, "type": "completion"},
    )
    assert response.status_code == 200

    response = client.get(f"/habits/{habit_id}/logs")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["status"] == True
    assert logs[0]["habit_type"] == "completion"


def test_log_choice_habit():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Choice Habit",
            "type": "choice",
            "options": [
                {"option_text": "Option 1", "color": "red", "icon": "icon1"},
                {
                    "option_text": "Option 2",
                },
            ],
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.get("/habits")
    option_id = response.json()[0]["options"][0]["id"]

    response = client.post(
        f"/log/{habit_id}",
        json={
            "log_date": "2024-01-01T00:00:00Z",
            "option_id": option_id,
            "type": "choice",
        },
    )
    entry_id = response.json()["id"]
    assert response.status_code == 200

    response = client.get(f"/log/{entry_id}")
    assert response.status_code == 200
    log_entry = response.json()
    assert log_entry["option"]["id"] == option_id
    assert log_entry["habit_type"] == "choice"

def test_delete_habit():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Completion Habit",
            "type": "completion",
            "completion_target": 1,
            "target_timeframe": "day",
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.delete(f"/habits/{habit_id}")
    assert response.status_code == 200

def test_delete_habit_deletes_logs_and_options():
    # Create a choice habit with an option and a log
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Choice Habit",
            "type": "choice",
            "options": [
                {"option_text": "Option 1", "color": "red", "icon": "icon1"},
            ],
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.get("/habits")
    option_id = response.json()[0]["options"][0]["id"]

    response = client.post(
        f"/log/{habit_id}",
        json={
            "log_date": "2024-01-01T00:00:00Z",
            "option_id": option_id,
            "type": "choice",
        },
    )
    assert response.status_code == 200

    # Delete the habit
    response = client.delete(f"/habits/{habit_id}")
    assert response.status_code == 200

    # Check that the habit is deleted
    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()
    assert len(habits) == 0

    # Check that the log is deleted
    response = client.get(f"/log/{habit_id}")
    assert response.status_code == 404

def test_delete_option():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Choice Habit",
            "type": "choice",
            "options": [
                {"option_text": "Option 1", "color": "red", "icon": "icon1"},
                {
                    "option_text": "Option 2",
                },
            ],
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()
    option_id_1 = habits[0]["options"][0]["id"]
    option_id_2 = habits[0]["options"][1]["id"]

    response = client.delete(f"/habits/{habit_id}/options/{option_id_1}")
    assert response.status_code == 200

    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()
    assert len(habits[0]["options"]) == 1
    assert habits[0]["options"][0]["id"] == option_id_2

def test_delete_log_entry():
    response = client.post(
        "/habits/new",
        json={
            "name": "Test Completion Habit",
            "type": "completion",
            "completion_target": 1,
            "target_timeframe": "day",
        },
    )
    assert response.status_code == 201
    habit_id = response.json()["id"]

    response = client.post(
        f"/log/{habit_id}",
        json={"log_date": "2024-01-01T00:00:00Z", "status": True, "type": "completion"},
    )
    assert response.status_code == 200
    log_id = response.json()["id"]

    response = client.delete(f"/log/{log_id}")
    assert response.status_code == 200

    response = client.get(f"/habits/{habit_id}/logs")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 0