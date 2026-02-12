import itertools
import pytest


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

# Ensure all fields are required when creating a completion habit
@pytest.mark.parametrize(
    "include",
    itertools.chain(
        *[
            itertools.combinations(
                ["name", "habit_type", "completion_target", "target_timeframe"], n
            )
            for n in range(4)
        ]
    ),
)
def test_disallow_creating_completion_habit_missing_fields(client, include):
    body = {
        "name": "Incomplete Habit",
        "habit_type": "completion",
        "target_timeframe": "day",
        "completion_target": 1,
    }
    response = client.post(
        "/habits/new",
        json={k: v for k, v in body.items() if k in include},
    )
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.parametrize(
    "include",
    itertools.chain(
        *[
            itertools.combinations(
                ["name", "habit_type", "target", "completion_target", "unit"], n
            )
            for n in range(5)
        ]
    ),
)
def test_disallow_creating_measurable_habit_missing_fields(client, include):
    body = {
        "name": "Incomplete Measurable Habit",
        "habit_type": "measurable",
        "target": 100,
        "completion_target": "day",
        "unit": "units",
    }
    response = client.post("/habits/new", json={k: v for k, v in body.items() if k in include})
    assert response.status_code == 422  # Unprocessable Entity