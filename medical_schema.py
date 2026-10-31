
from pydantic import BaseModel, Field


class MedicalContext(BaseModel):

    confirmed_conditions: list[str] = Field(
        default_factory=list
    )

    unconfirmed_conditions: list[str] = Field(
        default_factory=list
    )

    allergies: list[str] = Field(
        default_factory=list
    )

    medications: list[str] = Field(
        default_factory=list
    )

    current_symptoms: list[str] = Field(
        default_factory=list
    )
