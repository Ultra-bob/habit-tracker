import pytest


def test_correct_completion_log_entry_creation(client, example_habits):
    # Create a log entry for the first habit
    response = client.post(
        "/log/1", json={"timestamp": "2024-01-01 00:00:00", "status": True}
    )
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
    response = client.post(
        "/log/4", json={"timestamp": "2024-01-01 00:00:00", "amount": 1500}
    )
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
    response = client.post(
        "/log/6", json={"timestamp": "2024-01-01 00:00:00", "option_id": 1}
    )
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
    ],
)
def test_prevent_mismatched_log_entry_creation(
    client, example_habits, log_type, habit_type
):
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


@pytest.mark.parametrize("habit_type", ["completion", "measurable", "choice"])
def test_prevent_log_entry_creation_for_nonexistent_habit(client, habit_type):
    # Try to create a log entry for a non-existent habit
    if habit_type == "completion":
        log_data = {"timestamp": "2024-01-01 00:00:00", "status": True}
    elif habit_type == "measurable":
        log_data = {"timestamp": "2024-01-01 00:00:00", "amount": 100}
    else:  # choice
        log_data = {"timestamp": "2024-01-01 00:00:00", "option_id": 1}

    response = client.post("/log/999", json=log_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Habit not found"


@pytest.mark.parametrize("habit_type", ["completion", "measurable", "choice"])
def test_prevent_log_entry_creation_with_only_timestamp(
    client, example_habits, habit_type
):
    # Try to create a log entry with only a timestamp
    log_data = {"timestamp": "2024-01-01 00:00:00"}
    habit_id = {
        "completion": 1,
        "measurable": 4,
        "choice": 6,
    }[habit_type]

    response = client.post(f"/log/{habit_id}", json=log_data)
    assert response.status_code == 422


def test_prevent_choice_log_entry_creation_with_nonexistent_option(
    client, example_habits
):
    # Try to create a choice log entry with an invalid option_id
    response = client.post(
        "/log/6", json={"timestamp": "2024-01-01 00:00:00", "option_id": 999}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Option not found"


def test_prevent_choice_log_entry_creation_with_option_from_different_habit(
    client, example_habits
):
    # Create a new choice option for a different habit
    response = client.post(
        "/habits/new",
        json={
            "name": "Other Choice Habit",
            "type": "choice",
            "options": [
                {"option_text": "Option A", "color": "red", "icon": "circle"},
                {"option_text": "Option B", "color": "blue", "icon": "square"},
            ],
        },
    )
    assert response.status_code == 201
    new_habit_id = response.json()["id"]

    # Get the option_id of the new habit's first option
    response = client.get(f"/habits/{new_habit_id}/options")
    assert response.status_code == 200
    new_option_id = response.json()[0]["id"]

    # Try to create a choice log entry with an option_id that belongs to a different habit
    response = client.post(
        "/log/6", json={"timestamp": "2024-01-01 00:00:00", "option_id": new_option_id}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Option does not belong to the specified habit"


def test_prevent_log_entry_creation_with_invalid_timestamp(client, example_habits):
    # Try to create a log entry with an invalid timestamp
    response = client.post(
        "/log/1", json={"timestamp": "invalid-timestamp", "status": True}
    )
    assert response.status_code == 422


def test_get_logs_for_nonexistent_habit(client):
    # Try to get logs for a non-existent habit
    response = client.get("/log/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Habit not found"
