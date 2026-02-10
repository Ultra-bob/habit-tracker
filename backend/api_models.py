from pydantic import BaseModel, Field, create_model
from typing import Literal, Annotated, get_origin, Optional
from db_models import HabitType, Timeframe
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


class HabitOptions(BaseModel):
    name: str


class CompletionHabitOptions(HabitOptions):
    type: Literal[HabitType.COMPLETION] = HabitType.COMPLETION
    completion_target: int
    target_timeframe: Timeframe


class MeasureableHabitOptions(HabitOptions):
    type: Literal[HabitType.MEASURABLE] = HabitType.MEASURABLE
    target: int
    completion_target: Timeframe
    unit: str


class ChoiceHabitOptions(HabitOptions):
    type: Literal[HabitType.CHOICE] = HabitType.CHOICE
    options: list[ChoiceHabitOption]


def make_patch_model(
    model: type[BaseModel], *, discriminator: str | None = "type"
) -> type[BaseModel]:
    """
    Create a PATCH version of `model`:
    - all fields optional (default None)
    - except the discriminator field, which is kept as-is so unions still work
    """
    defs = {}

    for name, field in model.model_fields.items():
        ann = field.annotation

        if name == discriminator:
            # keep required/const-ish discriminator so Pydantic can choose the union variant
            defs[name] = (ann, field.default)
            continue

        # make optional unless already optional
        if get_origin(ann) is Optional or (get_origin(ann) is type(None)):
            opt_ann = ann
        else:
            opt_ann = ann | None  # py3.10+
        defs[name] = (opt_ann, None)

    return create_model(f"{model.__name__}Patch", **defs)


CompletionHabitPatch = make_patch_model(CompletionHabitOptions)
MeasureableHabitPatch = make_patch_model(MeasureableHabitOptions)
ChoiceHabitPatch = make_patch_model(ChoiceHabitOptions)

ChoiceHabitOptionPatch = make_patch_model(ChoiceHabitOption, discriminator=None)

HabitInput = Annotated[
    CompletionHabitOptions | MeasureableHabitOptions | ChoiceHabitOptions,
    Field(discriminator="type"),
]

HabitPatch = Annotated[
    CompletionHabitPatch | MeasureableHabitPatch | ChoiceHabitPatch,
    Field(discriminator="type"),
]

# Requiring the caller to provide the type makes sense for creating a new habit, but for logging, it is redundant.
# We could infer the type, but then we would lose FastAPI's automatic validation.
# Something to consider later...
HabitLog = Annotated[
    CompletionHabitLog | MeasureableHabitLog | ChoiceHabitLog,
    Field(discriminator="type"),
]
