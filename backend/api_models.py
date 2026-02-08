from pydantic import BaseModel, Field
from typing import Literal, Annotated
from models import HabitType, Timeframe
from datetime import datetime

class HabitLog(BaseModel):
    habit_id: int
    log_date: datetime

class NewHabit(BaseModel):
    name: str

class NewCompletionHabit(NewHabit):
    type: Literal[HabitType.COMPLETION] = HabitType.COMPLETION
    completion_target: int
    target_timeframe: Timeframe

class NewMeasureableHabit(NewHabit):
    type: Literal[HabitType.MEASURABLE] = HabitType.MEASURABLE
    target: int
    unit: str

HabitInput = Annotated[
    NewCompletionHabit | NewMeasureableHabit,
    Field(discriminator="type")
]