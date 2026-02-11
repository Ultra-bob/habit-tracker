def test_example_habits_creation(client, example_habits):
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


def test_update_completion_habit(client, example_habits):
    # Update the name of the first habit
    response = client.patch("/habits/1", json={"name": "Morning Medicine"})
    assert response.status_code == 200

    # Get the updated habit and check the name was changed
    response = client.get("/habits/1")
    assert response.status_code == 200
    habit = response.json()
    assert habit["name"] == "Morning Medicine"


def test_update_weekly_completion_habit(client, example_habits):
    # Update the completion target of the second habit
    response = client.patch("/habits/2", json={"completion_target": 4})
    assert response.status_code == 200

    # Get the updated habit and check the completion target was changed
    response = client.get("/habits/2")
    assert response.status_code == 200
    habit = response.json()
    assert habit["completion_target"] == 4


def test_update_completion_timeframe(client, example_habits):
    # Update the target timeframe of the third habit
    response = client.patch("/habits/3", json={"target_timeframe": "week"})
    assert response.status_code == 200

    # Get the updated habit and check the target timeframe was changed
    response = client.get("/habits/3")
    assert response.status_code == 200
    habit = response.json()
    assert habit["target_timeframe"] == "week"


def test_update_measurable_habit(client, example_habits):
    # Update the target of the fourth habit
    response = client.patch("/habits/4", json={"target": 2500})
    assert response.status_code == 200

    # Get the updated habit and check the target was changed
    response = client.get("/habits/4")
    assert response.status_code == 200
    habit = response.json()
    assert habit["target"] == 2500


def test_update_measurable_habit_timeframe(client, example_habits):
    # Update the completion target of the fifth habit
    response = client.patch("/habits/5", json={"completion_target": "day"})
    assert response.status_code == 200

    # Get the updated habit and check the completion target was changed
    response = client.get("/habits/5")
    assert response.status_code == 200
    habit = response.json()
    assert habit["completion_target"] == "day"


def test_update_choice_habit_name(client, example_habits):
    # Update the name of the sixth habit
    response = client.patch("/habits/6", json={"name": "Daily Mood"})
    assert response.status_code == 200

    # Get the updated habit and check the name was changed
    response = client.get("/habits/6")
    assert response.status_code == 200
    habit = response.json()
    assert habit["name"] == "Daily Mood"


def test_disallow_change_habit_type(client, example_habits):
    # Try to change the type of the first habit
    response = client.patch("/habits/1", json={"type": "measurable"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Changing habit type is not supported"


def test_disallow_invalid_update(client, example_habits):
    # Try to update a habit with an invalid field
    response = client.patch("/habits/1", json={"invalid_field": "value"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error


def test_disallow_update_option_of_other_habit_types(client, example_habits):
    # Try to update the unit of the first habit, which is a completion habit and doesn't have a unit field
    response = client.patch(
        "/habits/1",
        json={"unit": "mg"},
    )
    assert response.status_code == 400  # Unprocessable Entity due to validation error
