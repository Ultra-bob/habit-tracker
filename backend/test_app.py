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


def create_example_habits(client):
    """
    Helper function to create a variety of habits to avoid duplicating code in tests.
    """

    # Create a simple completion habit
    assert (
        client.post(
            "/habits/new",
            json={
                "type": "completion",
                "name": "Medicine",
                "completion_target": 1,
                "target_timeframe": "day",
            },
        ).status_code
        == 201
    )

    # Create a weekly completion habit
    assert (
        client.post(
            "/habits/new",
            json={
                "type": "completion",
                "name": "Exercise",
                "completion_target": 3,
                "target_timeframe": "week",
            },
        ).status_code
        == 201
    )

    # Create a twice daily completion habit
    assert (
        client.post(
            "/habits/new",
            json={
                "type": "completion",
                "name": "Flossing",
                "completion_target": 2,
                "target_timeframe": "day",
            },
        ).status_code
        == 201
    )

    # Create a measureable habit
    assert (
        client.post(
            "/habits/new",
            json={
                "type": "measurable",
                "name": "Water Intake",
                "target": 2000,
                "completion_target": "day",
                "unit": "ml",
            },
        ).status_code
        == 201
    )

    # Create a monthly measureable habit
    assert (
        client.post(
            "/habits/new",
            json={
                "type": "measurable",
                "name": "Pages Read",
                "target": 1000,
                "completion_target": "month",
                "unit": "pages",
            },
        ).status_code
        == 201
    )

    # Create a choice habit
    assert (
        client.post(
            "/habits/new",
            json={
                "type": "choice",
                "name": "Mood",
                "options": [
                    {"option_text": "Happy", "color": "yellow", "icon": "smile"},
                    {"option_text": "Sad", "color": "blue", "icon": "frown"},
                    {"option_text": "Neutral", "color": "gray", "icon": "meh"},
                ],
            },
        ).status_code
        == 201
    )

#* Uses the example data to test all the creation endpoints at once

def test_example_habits_creation():
    create_example_habits(client)

    # get all habits and check they were created correctly
    response = client.get("/habits")
    assert response.status_code == 200
    habits = response.json()

    # print(habits)  # Add this line to print the response for debugging

    assert len(habits) == 6
    assert habits == [
        {
            "id": 1,
            "name": "Medicine",
            "habit_type": "completion",
            "completion_target": 1,
            "target_timeframe": "day",
        },
        {
            "id": 2,
            "name": "Exercise",
            "habit_type": "completion",
            "completion_target": 3,
            "target_timeframe": "week",
        },
        {
            "id": 3,
            "name": "Flossing",
            "habit_type": "completion",
            "completion_target": 2,
            "target_timeframe": "day",
        },
        {
            "id": 4,
            "name": "Water Intake",
            "habit_type": "measurable",
            "target": 2000,
            "completion_target": "day",
            "unit": "ml",
        },
        {
            "id": 5,
            "name": "Pages Read",
            "habit_type": "measurable",
            "target": 1000,
            "completion_target": "month",
            "unit": "pages",
        },
        {
            "id": 6,
            "name": "Mood",
            "habit_type": "choice",
            "options": [
                {
                    "option_text": "Happy",
                    "color": "yellow",
                    "icon": "smile",
                    "id": 1,
                    "habit_id": 6,
                },
                {
                    "option_text": "Sad",
                    "color": "blue",
                    "icon": "frown",
                    "id": 2,
                    "habit_id": 6,
                },
                {
                    "option_text": "Neutral",
                    "color": "gray",
                    "icon": "meh",
                    "id": 3,
                    "habit_id": 6,
                },
            ],
        },
    ]

#* Tests for updating habits

def test_update_completion_habit():
    create_example_habits(client)

    # Update the name of the first habit
    response = client.patch("/habits/1", json={"name": "Morning Medicine"})
    assert response.status_code == 200

    # Get the updated habit and check the name was changed
    response = client.get("/habits/1")
    assert response.status_code == 200
    habit = response.json()
    assert habit["name"] == "Morning Medicine"


def test_update_weekly_completion_habit():
    create_example_habits(client)

    # Update the completion target of the second habit
    response = client.patch("/habits/2", json={"completion_target": 4})
    assert response.status_code == 200

    # Get the updated habit and check the completion target was changed
    response = client.get("/habits/2")
    assert response.status_code == 200
    habit = response.json()
    assert habit["completion_target"] == 4


def test_update_completion_timeframe():
    create_example_habits(client)

    # Update the target timeframe of the third habit
    response = client.patch("/habits/3", json={"target_timeframe": "week"})
    assert response.status_code == 200

    # Get the updated habit and check the target timeframe was changed
    response = client.get("/habits/3")
    assert response.status_code == 200
    habit = response.json()
    assert habit["target_timeframe"] == "week"

def test_update_measurable_habit():
    create_example_habits(client)

    # Update the target of the fourth habit
    response = client.patch("/habits/4", json={"target": 2500})
    assert response.status_code == 200

    # Get the updated habit and check the target was changed
    response = client.get("/habits/4")
    assert response.status_code == 200
    habit = response.json()
    assert habit["target"] == 2500

def test_update_measurable_habit_timeframe():
    create_example_habits(client)

    # Update the completion target of the fifth habit
    response = client.patch("/habits/5", json={"completion_target": "day"})
    assert response.status_code == 200

    # Get the updated habit and check the completion target was changed
    response = client.get("/habits/5")
    assert response.status_code == 200
    habit = response.json()
    assert habit["completion_target"] == "day"

def test_update_choice_habit_name():
    create_example_habits(client)

    # Update the name of the sixth habit
    response = client.patch("/habits/6", json={"name": "Daily Mood"})
    assert response.status_code == 200

    # Get the updated habit and check the name was changed
    response = client.get("/habits/6")
    assert response.status_code == 200
    habit = response.json()
    assert habit["name"] == "Daily Mood"

def test_disallow_change_habit_type():
    create_example_habits(client)

    # Try to change the type of the first habit
    response = client.patch("/habits/1", json={"type": "measurable"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Changing habit type is not supported"

def test_disallow_invalid_update():
    create_example_habits(client)

    # Try to update a habit with an invalid field
    response = client.patch("/habits/1", json={"invalid_field": "value"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error

def test_disallow_update_option_of_other_habit_types():
    create_example_habits(client)

    # Try to update the unit of the first habit, which is a completion habit and doesn't have a unit field
    response = client.patch(
        "/habits/1",
        json={ "unit": "mg" },
    )
    assert response.status_code == 400  # Unprocessable Entity due to validation error

#* Tests for options on choice habits

def test_disallow_option_update_through_habit_endpoint():
    create_example_habits(client)

    # Try to update the options of the choice habit through the habit endpoint
    response = client.patch(
        "/habits/6",
        json={
            "options": [
                {"option_text": "Ecstatic", "color": "bright yellow", "icon": "grin"},
                {"option_text": "Miserable", "color": "dark blue", "icon": "sob"},
            ]
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Updating options through this endpoint is not supported"

def test_add_choice_option():
    create_example_habits(client)

    # Add a new option to the choice habit
    response = client.post(
        "/habits/6/options",
        json={"option_text": "Anxious", "color": "purple", "icon": "sad"},
    )
    assert response.status_code == 201

    # Get the updated habit and check the new option was added
    response = client.get("/habits/6")
    assert response.status_code == 200
    habit = response.json()
    assert len(habit["options"]) == 4
    assert habit["options"][-1]["option_text"] == "Anxious"
    assert habit["options"][-1]["color"] == "purple"
    assert habit["options"][-1]["icon"] == "sad"

def test_update_choice_option():
    create_example_habits(client)

    # Update the first option of the choice habit
    response = client.patch(
        "/habits/6/options/1",
        json={"option_text": "Very Happy", "color": "bright yellow"},
    )
    assert response.status_code == 200

    # Get the updated habit and check the option was updated
    response = client.get("/habits/6")
    assert response.status_code == 200
    habit = response.json()
    assert habit["options"][0]["option_text"] == "Very Happy"
    assert habit["options"][0]["color"] == "bright yellow"
    assert habit["options"][0]["icon"] == "smile"  # unchanged

def test_delete_choice_option():
    create_example_habits(client)

    # Delete the second option of the choice habit
    response = client.delete("/habits/6/options/2")
    assert response.status_code == 200

    # Get the updated habit and check the option was deleted
    response = client.get("/habits/6")
    assert response.status_code == 200
    habit = response.json()
    assert len(habit["options"]) == 2
    assert all(option["option_text"] != "Sad" for option in habit["options"])

def test_delete_choice_option_invalid_habit():
    create_example_habits(client)

    # Try to delete an option from a non-choice habit
    response = client.delete("/habits/1/options/1")
    assert response.status_code == 400
    assert response.json()["detail"] == "Habit is not a choice habit"

def test_delete_choice_option_not_found():
    create_example_habits(client)

    # Try to delete a non-existent option from the choice habit
    response = client.delete("/habits/6/options/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Option not found for this habit"

def test_update_choice_option_invalid_habit():
    create_example_habits(client)

    # Try to update an option from a non-choice habit
    response = client.patch(
        "/habits/1/options/1",
        json={"option_text": "Very Happy", "color": "bright yellow"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Habit is not a choice habit"

def test_update_choice_option_not_found():
    create_example_habits(client)

    # Try to update a non-existent option from the choice habit
    response = client.patch(
        "/habits/6/options/999",
        json={"option_text": "Very Happy", "color": "bright yellow"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Option not found for this habit"

def test_add_choice_option_invalid_habit():
    create_example_habits(client)

    # Try to add an option to a non-choice habit
    response = client.post(
        "/habits/1/options",
        json={"option_text": "Anxious", "color": "purple", "icon": "sad"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Habit is not a choice habit"

def test_add_choice_option_habit_not_found():
    create_example_habits(client)

    # Try to add an option to a non-existent habit
    response = client.post(
        "/habits/999/options",
        json={"option_text": "Anxious", "color": "purple", "icon": "sad"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Habit not found"