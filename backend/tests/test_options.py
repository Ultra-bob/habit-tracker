def test_disallow_option_update_through_habit_endpoint(client, example_habits):
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
    assert (
        response.json()["detail"]
        == "Updating options through this endpoint is not supported"
    )


def test_add_choice_option(client, example_habits):
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


def test_update_choice_option(client, example_habits):
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


def test_delete_choice_option(client, example_habits):
    # Delete the second option of the choice habit
    response = client.delete("/habits/6/options/2")
    assert response.status_code == 200

    # Get the updated habit and check the option was deleted
    response = client.get("/habits/6")
    assert response.status_code == 200
    habit = response.json()
    assert len(habit["options"]) == 2
    assert all(option["option_text"] != "Sad" for option in habit["options"])


def test_delete_choice_option_invalid_habit(client, example_habits):
    # Try to delete an option from a non-choice habit
    response = client.delete("/habits/1/options/1")
    assert response.status_code == 400
    assert response.json()["detail"] == "Habit is not a choice habit"


def test_delete_choice_option_not_found(client, example_habits):
    # Try to delete a non-existent option from the choice habit
    response = client.delete("/habits/6/options/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Option not found for this habit"


def test_update_choice_option_invalid_habit(client, example_habits):
    # Try to update an option from a non-choice habit
    response = client.patch(
        "/habits/1/options/1",
        json={"option_text": "Very Happy", "color": "bright yellow"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Habit is not a choice habit"


def test_update_choice_option_not_found(client, example_habits):
    # Try to update a non-existent option from the choice habit
    response = client.patch(
        "/habits/6/options/999",
        json={"option_text": "Very Happy", "color": "bright yellow"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Option not found for this habit"


def test_add_choice_option_invalid_habit(client, example_habits):
    # Try to add an option to a non-choice habit
    response = client.post(
        "/habits/1/options",
        json={"option_text": "Anxious", "color": "purple", "icon": "sad"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Habit is not a choice habit"


def test_add_choice_option_habit_not_found(client, example_habits):
    # Try to add an option to a non-existent habit
    response = client.post(
        "/habits/999/options",
        json={"option_text": "Anxious", "color": "purple", "icon": "sad"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Habit not found"
