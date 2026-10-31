from memory_db import (
    initialize_memory_db,
    save_approved_context,
    get_approved_context
)
from extract_context import extract_medical_context

# Fictional test message
message = (
    "I think I might have diabetes. "
    "I'm allergic to penicillin. "
    "I've been feeling thirsty."
)

# Extract structured medical data
extracted = extract_medical_context(message)

print("\nEXTRACTED MEDICAL CONTEXT")
print(extracted.model_dump_json(indent=4))

initialize_memory_db()

# Ask for confirmation
choice = input("\nSave this information? (yes/no): ")

if choice.strip().lower() == "yes":
    approved_context = extracted.model_dump()

    save_approved_context(approved_context)

    print("\nApproved context saved to SQLite!")

    print("\nStored records:")
    print(get_approved_context())

else:
    print("\nInformation rejected. Nothing saved.")