import sqlalchemy
from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from sqlalchemy import create_engine
from enum import StrEnum


class HabitType(StrEnum):
    COMPLETION = "completion"
    MEASURABLE = "measurable"
    CHOICE = "choice"


class Timeframe(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class Base(DeclarativeBase, SerializerMixin):
    pass


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    habit_type: Mapped[HabitType] = mapped_column(SQLEnum(HabitType), nullable=False)

    logs: Mapped[list["LogEntry"]] = relationship(
        back_populates="habit",
        cascade="all, delete-orphan",
    )

    __mapper_args__ = {"polymorphic_identity": None, "polymorphic_on": habit_type}

    def to_dict(self):  # ty:ignore[invalid-method-override] #? Again, this is (probably) fine, why is there a type error?
        return super().to_dict(rules=("-logs", "-options.habit"))


class CompletionHabit(Habit):
    __tablename__ = "completion_habits"

    id: Mapped[int] = mapped_column(ForeignKey("habits.id"), primary_key=True)
    completion_target: Mapped[int] = mapped_column()
    target_timeframe: Mapped[Timeframe] = mapped_column(SQLEnum(Timeframe))

    __mapper_args__ = {"polymorphic_identity": HabitType.COMPLETION}


class MeasureableHabit(Habit):
    __tablename__ = "measureable_habits"

    id: Mapped[int] = mapped_column(ForeignKey("habits.id"), primary_key=True)
    target: Mapped[int] = mapped_column()
    unit: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {"polymorphic_identity": HabitType.MEASURABLE}


class ChoiceOption(Base):
    __tablename__ = "choice_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("choice_habits.id", ondelete="CASCADE"), nullable=False
    )

    habit: Mapped["ChoiceHabit"] = relationship(back_populates="options")

    option_text: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(20), nullable=True)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)


class ChoiceHabit(Habit):
    __tablename__ = "choice_habits"

    id: Mapped[int] = mapped_column(ForeignKey("habits.id"), primary_key=True)
    options: Mapped[list[ChoiceOption]] = relationship(
        back_populates="habit",
        cascade="all, delete-orphan",
    )

    __mapper_args__ = {"polymorphic_identity": HabitType.CHOICE}


class LogEntry(Base):
    __tablename__ = "habit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )
    habit: Mapped[Habit] = relationship(back_populates="logs")
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    habit_type: Mapped[HabitType] = mapped_column(SQLEnum(HabitType), nullable=False)

    __mapper_args__ = {"polymorphic_identity": None, "polymorphic_on": habit_type}

    def to_dict(self):  # ty:ignore[invalid-method-override] #? ditto
        base_dict = super().to_dict(rules=("-habit", "-option.habit"))
        # if self.habit_type == HabitType.CHOICE:
        #     base_dict["option"] = self.option.to_dict()
        return base_dict


class CompletionLogEntry(LogEntry):
    __tablename__ = "completion_logs"

    id: Mapped[int] = mapped_column(ForeignKey("habit_logs.id"), primary_key=True)
    status: Mapped[bool] = mapped_column()

    __mapper_args__ = {"polymorphic_identity": HabitType.COMPLETION}


class MeasureableLogEntry(LogEntry):
    __tablename__ = "measureable_logs"

    id: Mapped[int] = mapped_column(ForeignKey("habit_logs.id"), primary_key=True)
    value: Mapped[int] = mapped_column()

    __mapper_args__ = {"polymorphic_identity": HabitType.MEASURABLE}


class ChoiceLogEntry(LogEntry):
    __tablename__ = "choice_logs"

    id: Mapped[int] = mapped_column(ForeignKey("habit_logs.id"), primary_key=True)

    option_id: Mapped[int] = mapped_column(
        ForeignKey("choice_options.id"), nullable=False
    )
    option: Mapped[ChoiceOption] = relationship()

    __mapper_args__ = {"polymorphic_identity": HabitType.CHOICE}


def get_engine() -> sqlalchemy.engine.Engine:
    engine = create_engine(
        "sqlite:///habits.db", echo=True
    )  # Use an in-memory SQLite database for example
    Base.metadata.create_all(engine)
    return engine
