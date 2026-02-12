import pytest
def test_correct_completion_log_entry_creation(client, example_habits):
    # Create a log entry for the first habit
    response = client.post("/log/1", json={"timestamp": "2024-01-01 00:00:00", "status": True})
    assert response.status_code == 201

    # Get the log entries for the first habit and check the entry was created correctly
    response = client.get("/log/1")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0] == {
        "id": 1,
        "habit_id": 1,
        "timestamp": "2024-01-01 00:00:00",
        "status": True,
        "habit_type": "completion",
    }

def test_correct_measureable_log_entry_creation(client, example_habits):
    # Create a log entry for the fourth habit
    response = client.post("/log/4", json={"timestamp": "2024-01-01 00:00:00", "amount": 1500})
    assert response.status_code == 201

    # Get the log entries for the fourth habit and check the entry was created correctly
    response = client.get("/log/4")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0] == {
        "id": 1,
        "habit_id": 4,
        "timestamp": "2024-01-01 00:00:00",
        "value": 1500,
        "habit_type": "measurable",
    }

def test_correct_choice_log_entry_creation(client, example_habits):
    # Create a log entry for the sixth habit
    response = client.post("/log/6", json={"timestamp": "2024-01-01 00:00:00", "option_id": 1})
    assert response.status_code == 201

    # Get the log entries for the sixth habit and check the entry was created correctly
    response = client.get("/log/6")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0] == {
        "id": 1,
        "habit_id": 6,
        "timestamp": "2024-01-01 00:00:00",
        "option_id": 1,
        "option": {
            "id": 1,
            "habit_id": 6,
            "option_text": "Happy",
            "color": "yellow",
            "icon": "smile",
        },
        "habit_type": "choice",
    }

@pytest.mark.parametrize(
    "log_type, habit_type",
    [
        ("completion", "measurable"),
        ("completion", "choice"),
        ("measurable", "completion"),
        ("measurable", "choice"),
        ("choice", "completion"),
        ("choice", "measurable"),
    ]
)
def test_prevent_mismatched_log_entry_creation(client, example_habits, log_type, habit_type):
    # Try to create a log entry with a mismatched habit type
    if log_type == "completion":
        log_data = {"timestamp": "2024-01-01 00:00:00", "status": True}
    elif log_type == "measurable":
        log_data = {"timestamp": "2024-01-01 00:00:00", "amount": 100}
    else:  # choice
        log_data = {"timestamp": "2024-01-01 00:00:00", "option_id": 1}

    habit_id = {
        "completion": 1,
        "measurable": 4,
        "choice": 6,
    }[habit_type]

    response = client.post(f"/log/{habit_id}", json=log_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Habit type mismatch"