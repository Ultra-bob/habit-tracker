from pydantic import BaseModel, Field
from typing import Literal, Annotated
from models import HabitType, Timeframe
from datetime import datetime


class HabitLogBase(BaseModel):
    log_date: datetime


class CompletionHabitLog(HabitLogBase):
    type: Literal[HabitType.COMPLETION] = HabitType.COMPLETION
    status: bool


class MeasureableHabitLog(HabitLogBase):
    type: Literal[HabitType.MEASURABLE] = HabitType.MEASURABLE
    amount: int


class ChoiceHabitLog(HabitLogBase):
    type: Literal[HabitType.CHOICE] = HabitType.CHOICE
    option_id: int


class ChoiceHabitOption(BaseModel):
    option_text: str
    color: str | None = None
    icon: str | None = None


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


class NewChoiceHabit(NewHabit):
    type: Literal[HabitType.CHOICE] = HabitType.CHOICE
    options: list[ChoiceHabitOption]


HabitInput = Annotated[
    NewCompletionHabit | NewMeasureableHabit | NewChoiceHabit,
    Field(discriminator="type"),
]

# Requiring the caller to provide the type makes sense for creating a new habit, but for logging, it is redundant.
# We could infer the type, but then we would lose FastAPI's automatic validation.
# Something to consider later...
HabitLog = Annotated[
    CompletionHabitLog | MeasureableHabitLog | ChoiceHabitLog,
    Field(discriminator="type"),
]
