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


test_client = TestClient(app.app)


@pytest.fixture
def client() -> TestClient:
    return test_client


@pytest.fixture
def example_habits(client):
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
