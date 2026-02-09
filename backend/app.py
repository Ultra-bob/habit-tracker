from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import get_engine
from sqlalchemy.orm import sessionmaker, Session
import api_models as a  # Shortcut for "API models", reduces confusion compared to importing without alias
import models as d  # Shortcut for "database models"

app = FastAPI()

# Necessary to prevent initializing the production database when running tests, since the test suite monkeypatches this variable
db: sessionmaker[Session] = None  # ty: ignore[invalid-assignment]

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"])  # ty: ignore[invalid-argument-type] #? Why is this an error


@app.post("/habits/new", status_code=201)
def create_habit(habit: a.HabitInput):
    if isinstance(habit, a.NewCompletionHabit):
        with db() as session:
            session.add(d.CompletionHabit(**habit.model_dump(exclude={"type"})))
            session.commit()
    elif isinstance(habit, a.NewMeasureableHabit):
        with db() as session:
            session.add(d.MeasureableHabit(**habit.model_dump(exclude={"type"})))
            session.commit()
    elif isinstance(habit, a.NewChoiceHabit):
        with db() as session:
            choice_habit = d.ChoiceHabit(
                **habit.model_dump(exclude={"type", "options"})
            )
            session.add(choice_habit)
            session.commit()

            for option in habit.options:
                choice_option = d.ChoiceOption(
                    **option.model_dump(), habit_id=choice_habit.id
                )
                session.add(choice_option)
            session.commit()
    # ? Will FastAPI guarantee that this case is impossible?


@app.post("/log/{id}")
def log_habit(id: int, log: a.HabitLog):
    with db() as session:
        habit = session.get(d.Habit, id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        if habit.habit_type != log.type:
            raise HTTPException(status_code=400, detail="Habit type mismatch")
        if isinstance(log, a.CompletionHabitLog):
            entry = d.CompletionLogEntry(
                habit_id=id,
                recorded_at=log.log_date,
                status=log.status,
                habit_type=d.HabitType.COMPLETION,
            )
        elif isinstance(log, a.MeasureableHabitLog):
            entry = d.MeasureableLogEntry(
                habit_id=id,
                recorded_at=log.log_date,
                value=log.amount,
                habit_type=d.HabitType.MEASURABLE,
            )
        elif isinstance(log, a.ChoiceHabitLog):
            # Validation to ensure option belongs to the habit
            option = session.get(d.ChoiceOption, log.option_id)
            if option is None:
                raise HTTPException(status_code=404, detail="Option not found")
            if option.habit_id != id:
                raise HTTPException(
                    status_code=400,
                    detail="Option does not belong to the specified habit",
                )
            entry = d.ChoiceLogEntry(
                habit_id=id,
                recorded_at=log.log_date,
                option_id=log.option_id,
                habit_type=d.HabitType.CHOICE,
            )

        session.add(entry)
        session.commit()


@app.get("/log/{id}")
def get_logs(id: int):
    with db() as session:
        habit = session.get(d.Habit, id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")

        return [log.to_dict() for log in habit.logs]


@app.get("/habits")
def list_habits():
    with db() as session:
        habits = session.query(d.Habit).all()
        return [habit.to_dict() for habit in habits]


if __name__ == "__main__":
    engine = get_engine()
    db = sessionmaker(bind=engine)

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
