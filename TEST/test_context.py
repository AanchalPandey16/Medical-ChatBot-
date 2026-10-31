
from context_manager import get_context_by_tokens, count_tokens

messages = [
    {"role": "user", "content": "What is fever?"},
    {"role": "assistant", "content": "Fever is an increase in body temperature."},
    {"role": "user", "content": "What is diabetes?"},
    {"role": "assistant", "content": "Diabetes affects how the body regulates blood sugar."},
    {"role": "user", "content": "What are its symptoms?"}
]

selected = get_context_by_tokens(
    messages,
    max_tokens=30
)

print("SELECTED CONTEXT")
print("----------------")

for msg in selected:
    print(msg["role"], ":", msg["content"])

print()
print(
    "Total text tokens:",
    sum(count_tokens(msg["content"]) for msg in selected)
)
