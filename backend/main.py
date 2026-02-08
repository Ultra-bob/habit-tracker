from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Habit, CompletionHabit, MeasureableHabit, HabitLog, get_engine
from sqlalchemy.orm import sessionmaker
from api_models import HabitInput, NewMeasureableHabit, NewCompletionHabit

app = FastAPI()
engine = get_engine()
db = sessionmaker(bind=engine)

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"])
counter = 0


@app.post("/habits/new", status_code=201)
def create_habit(habit: HabitInput):
    if isinstance(habit, NewCompletionHabit):
        with db() as session:
            session.add(CompletionHabit(**habit.model_dump(exclude={"type"})))
            session.commit()
    elif isinstance(habit, NewMeasureableHabit):
        with db() as session:
            session.add(MeasureableHabit(**habit.model_dump(exclude={"type"})))
            session.commit()


@app.post("/log/{id}")
def log_habit(id: int, status: int):
    with db() as session:
        habit = session.get(Habit, id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")

        if isinstance(habit, CompletionHabit):
            if status != 1:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid status for completion habit. Must be 1.",
                )
        session.add(HabitLog(habit_id=id, status=status))
        session.commit()

@app.get("/log/{id}")
def get_logs(id: int):
    with db() as session:
        habit = session.get(Habit, id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        
        return habit.logs

@app.get("/habits")
def list_habits():
    with db() as session:
        habits = session.query(Habit).all()
        return [habit.to_dict() for habit in habits]
