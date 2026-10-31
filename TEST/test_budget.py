
from context_manager import build_context, count_tokens

system_prompt = "You are a medical information assistant."

previous_messages = [
    {"role": "user", "content": "What is fever?"},
    {"role": "assistant", "content": "Fever is elevated body temperature."},
    {"role": "user", "content": "What is diabetes?"},
    {"role": "assistant", "content": "Diabetes affects blood sugar levels."}
]

user_message = "What are its symptoms?"

result = build_context(
    system_prompt=system_prompt,
    previous_messages=previous_messages,
    user_message=user_message,
    total_budget=80,
    response_reserve=30,
    overhead_reserve=20
)

print("FINAL CONTEXT SENT TO AI")
print("------------------------")

for msg in result:
    print(msg["role"], ":", msg["content"])

total_tokens = sum(
    count_tokens(msg["content"]) for msg in result
)

print("\nSelected text tokens:", total_tokens)
