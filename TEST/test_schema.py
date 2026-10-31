
from medical_schema import MedicalContext
from pydantic import ValidationError

# Correct structure
valid_data = {
    "confirmed_conditions": [],
    "unconfirmed_conditions": ["diabetes"],
    "allergies": [],
    "medications": [],
    "current_symptoms": ["thirsty"]
}

validated = MedicalContext.model_validate(valid_data)

print("VALID DATA:")
print(validated.model_dump())

# Incorrect structure
invalid_data = {
    "allergies": "penicillin"
}

try:
    MedicalContext.model_validate(invalid_data)

except ValidationError as error:
    print("\nVALIDATION FAILED:")
    print(error.errors()[0]["msg"])
