import pytest

def test_get_completion_habit_daily_summary(client, example_habits):
    # Create some log entries for the first habit
    client.post("/log/1", json={"timestamp": "2024-01-01 00:00:00", "status": True})
    client.post("/log/1", json={"timestamp": "2024-01-01 12:00:00", "status": False})
    client.post("/log/1", json={"timestamp": "2024-01-02 00:00:00", "status": True})

    # Get the daily summary for the first habit and check the counts are correct
    response = client.get("/log/1/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary == {
        "2024-01-01": 2,
        "2024-01-02": 1,
    }

def test_get_measureable_habit_daily_summary(client, example_habits):
    # Create some log entries for the fourth habit
    client.post("/log/4", json={"timestamp": "2024-01-01 00:00:00", "amount": 1000})
    client.post("/log/4", json={"timestamp": "2024-01-01 12:00:00", "amount": 500})
    client.post("/log/4", json={"timestamp": "2022-01-05 00:00:00", "amount": 1500})

    # Get the daily summary for the fourth habit and check the totals are correct
    response = client.get("/log/4/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary == {
        "2024-01-01": 1500,
        "2022-01-05": 1500,
    }