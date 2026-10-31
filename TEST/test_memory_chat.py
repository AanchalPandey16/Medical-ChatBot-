
from memory_chat import (
    initialize_db,
    add_fact,
    get_facts,
    update_fact,
    delete_fact
)

initialize_db()

# Add facts to two different chats
add_fact(101, "allergies", "penicillin")
add_fact(102, "allergies", "amoxicillin")
add_fact(101, "unconfirmed_conditions", "diabetes")

print("CHAT 101:")
print(get_facts(101))

print("\nCHAT 102:")
print(get_facts(102))

# Try to delete Chat 102's first fact using Chat 101
chat_102_fact_id = get_facts(102)[0][0]

result = delete_fact(101, chat_102_fact_id)

print("\nCross-chat delete result:", result)

print("\nCHAT 102 AFTER ATTEMPT:")
print(get_facts(102))
