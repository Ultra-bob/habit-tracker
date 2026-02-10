from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db_models import get_engine
from sqlalchemy.orm import sessionmaker, Session
import api_models as a  # Shortcut for "API models", reduces confusion compared to importing without alias
import db_models as d  # Shortcut for "database models"

app = FastAPI()

# Necessary to prevent initializing the production database when running tests, since the test suite monkeypatches this variable
db: sessionmaker[Session] = None  # ty: ignore[invalid-assignment]

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"])  # ty: ignore[invalid-argument-type] #? Why is this an error


@app.post("/habits/new", status_code=201)
def create_habit(options: a.HabitInput):
    id = None
    if isinstance(options, a.CompletionHabitOptions):
        with db() as session:
            habit = d.CompletionHabit(**options.model_dump(exclude={"type"}))
            session.add(habit)
            session.commit()
            id = habit.id
    elif isinstance(options, a.MeasureableHabitOptions):
        with db() as session:
            habit = d.MeasureableHabit(**options.model_dump(exclude={"type"}))
            session.add(habit)
            session.commit()
            id = habit.id
    elif isinstance(options, a.ChoiceHabitOptions):
        with db() as session:
            habit = d.ChoiceHabit(
                **options.model_dump(exclude={"type", "options"})
            )
            session.add(habit)
            session.commit()

            for option in options.options:
                choice_option = d.ChoiceOption(
                    **option.model_dump(), habit_id=habit.id
                )
                session.add(choice_option)
            session.commit()
            id = habit.id
    # ? Will FastAPI guarantee that this case is impossible?

    return {"message": "Habit created", "id": id}

@app.patch("/habits/{id}")
def update_habit(id: int, habit: a.HabitPatch):
    with db() as session:
        existing_habit = session.get(d.Habit, id)
        if existing_habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        if existing_habit.habit_type != habit.type:
            raise HTTPException(status_code=400, detail="Changing habit type is not supported")

        update_data = habit.model_dump(exclude_unset=True, exclude={"type"})
        for key, value in update_data.items():
            setattr(existing_habit, key, value)
        session.commit()

@app.delete("/habits/{id}")
def delete_habit(id: int):
    with db() as session:
        habit = session.get(d.Habit, id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        session.delete(habit)
        session.commit()


@app.post("/habits/{id}/options")
def add_option(id: int, option: a.ChoiceHabitOption):
    with db() as session:
        habit = session.get(d.Habit, id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        if habit.habit_type != d.HabitType.CHOICE:
            raise HTTPException(status_code=400, detail="Habit is not a choice habit")

        choice_option = d.ChoiceOption(
            **option.model_dump(), habit_id=id
        )
        session.add(choice_option)
        session.commit()

@app.patch("/habits/{habit_id}/options/{option_id}")
def update_option(habit_id: int, option_id: int, option: a.ChoiceHabitOptionPatch):
    with db() as session:
        habit = session.get(d.Habit, habit_id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        if habit.habit_type != d.HabitType.CHOICE:
            raise HTTPException(status_code=400, detail="Habit is not a choice habit")

        existing_option = session.get(d.ChoiceOption, option_id)
        if existing_option is None or existing_option.habit_id != habit_id:
            raise HTTPException(status_code=404, detail="Option not found for this habit")

        update_data = option.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_option, key, value)
        session.commit()

@app.delete("/habits/{habit_id}/options/{option_id}")
def delete_option(habit_id: int, option_id: int):
    with db() as session:
        habit = session.get(d.Habit, habit_id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        if habit.habit_type != d.HabitType.CHOICE:
            raise HTTPException(status_code=400, detail="Habit is not a choice habit")

        existing_option = session.get(d.ChoiceOption, option_id)
        if existing_option is None or existing_option.habit_id != habit_id:
            raise HTTPException(status_code=404, detail="Option not found for this habit")

        session.delete(existing_option)
        session.commit()

@app.get("/habits/{id}")
def get_habit(id: int):
    with db() as session:
        habit = session.get(d.Habit, id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        return habit.to_dict()

@app.get("/habits/{id}/options")
def get_habit_options(id: int):
    with db() as session:
        habit = session.get(d.Habit, id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        if not isinstance(habit, d.ChoiceHabit):
            raise HTTPException(status_code=400, detail="Habit is not a choice habit")
        return [option.to_dict() for option in habit.options]

@app.get("/habits/{habit_id}/logs")
def get_habit_logs(habit_id: int):
    with db() as session:
        habit = session.get(d.Habit, habit_id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        return [log.to_dict() for log in habit.logs]

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
        return {"message": "Habit logged", "id": entry.id}


@app.get("/log/{id}")
def get_log_entry(id: int):
    with db() as session:
        entry = session.get(d.LogEntry, id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Log entry not found")
        return entry.to_dict()

@app.patch("/log/{id}")
def update_log_entry(id: int, log: a.HabitLogPatch):
    with db() as session:
        log_entry = session.get(d.LogEntry, id)
        if log_entry is None:
            raise HTTPException(status_code=404, detail="Log entry not found")
        if log_entry.habit_type != log.type:
            raise HTTPException(status_code=400, detail="Habit type mismatch")

        update_data = log.model_dump(exclude_unset=True, exclude={"type"})
        for key, value in update_data.items():
            setattr(log_entry, key, value)
        session.commit()

@app.delete("/log/{id}")
def delete_log_entry(id: int):
    with db() as session:
        log_entry = session.get(d.LogEntry, id)
        if log_entry is None:
            raise HTTPException(status_code=404, detail="Log entry not found")
        session.delete(log_entry)
        session.commit()

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
