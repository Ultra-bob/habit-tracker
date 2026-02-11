from pydantic import BaseModel, Field, create_model, ConfigDict
from typing import Literal, Annotated, get_origin, Optional
from db_models import HabitType, Timeframe
from datetime import datetime


class HabitLogBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    log_date: datetime

    @property
    def type(self) -> HabitType:
        raise NotImplementedError("Subclasses must define a type property")


class CompletionHabitLog(HabitLogBase):
    status: bool

    def type(self) -> HabitType:
        return HabitType.COMPLETION


class MeasureableHabitLog(HabitLogBase):
    amount: int

    def type(self) -> HabitType:
        return HabitType.MEASURABLE


class ChoiceHabitLog(HabitLogBase):
    option_id: int

    def type(self) -> HabitType:
        return HabitType.CHOICE


class ChoiceHabitOption(BaseModel):
    option_text: str
    color: str | None = None
    icon: str | None = None


class HabitOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str

    @staticmethod  # Necessary since the make_patch_model function doesn't preserve methods
    def inspect_type(self) -> HabitType | None:
        #! This is a bit hacky but allows us to avoid repeating the type field in every subclass
        if isinstance(self, (CompletionHabitOptions, CompletionHabitPatch)):
            return HabitType.COMPLETION
        elif isinstance(self, (MeasureableHabitOptions, MeasureableHabitPatch)):
            return HabitType.MEASURABLE
        elif isinstance(self, (ChoiceHabitOptions, ChoiceHabitPatch)):
            return HabitType.CHOICE
        else:
            return None


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
    - drop the discriminator field
    """
    defs = {}

    for name, field in model.model_fields.items():
        ann = field.annotation

        if name == discriminator:
            continue

        # make optional unless already optional
        if get_origin(ann) is Optional or (get_origin(ann) is type(None)):
            opt_ann = ann
        else:
            opt_ann = ann | None  # py3.10+
        defs[name] = (opt_ann, None)

    return create_model(
        f"{model.__name__}Patch",
        __base__=model,  # keeps any validators you defined on the original model
        __config__=ConfigDict(extra="forbid"),
        **defs,
    )


CompletionHabitPatch = make_patch_model(CompletionHabitOptions)
MeasureableHabitPatch = make_patch_model(MeasureableHabitOptions)
ChoiceHabitPatch = make_patch_model(ChoiceHabitOptions)

ChoiceHabitOptionPatch = make_patch_model(ChoiceHabitOption, discriminator=None)

HabitInput = Annotated[
    CompletionHabitOptions | MeasureableHabitOptions | ChoiceHabitOptions,
    Field(discriminator="type"),
]

HabitPatch = (
    HabitOptions | CompletionHabitPatch | MeasureableHabitPatch | ChoiceHabitPatch
)

HabitLog = CompletionHabitLog | MeasureableHabitLog | ChoiceHabitLog

CompletionHabitLogPatch = make_patch_model(CompletionHabitLog)
MeasureableHabitLogPatch = make_patch_model(MeasureableHabitLog)
ChoiceHabitLogPatch = make_patch_model(ChoiceHabitLog)

HabitLogPatch = CompletionHabitLogPatch | MeasureableHabitLogPatch | ChoiceHabitLogPatch
