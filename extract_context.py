
import os
from dotenv import load_dotenv
from openai import OpenAI
from medical_schema import MedicalContext

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))


def extract_medical_context(message):

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": """
                Extract medical information explicitly
                reported by the user.

                Do not diagnose or assume medical conditions.

                Classify uncertain conditions under
                unconfirmed_conditions.

                Treat confirmed_conditions as
                user-reported diagnoses, not independently
                verified medical diagnoses.

                Extract allergies, medications, and
                current symptoms only when reported.

                If a category has no information,
                return an empty list.

                Do not infer medical facts.
                """
            },
            {
                "role": "user",
                "content": message
            }
        ],

        response_format=MedicalContext,
        temperature=0
    )

    extracted = response.choices[0].message.parsed

    if extracted is None:
        raise ValueError("No structured medical data returned")

    return extracted


# Test with fictional data
if __name__ == "__main__":

    message = (
        "I think I might have diabetes. "
        "I'm allergic to penicillin. "
        "I've been feeling very thirsty."
    )

    result = extract_medical_context(message)

    print(result.model_dump_json(indent=4))
