
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o-mini")


def count_tokens(text):
    return len(encoding.encode(text))

def build_context(system_prompt, previous_messages, user_message, total_budget = 4000, response_reserve = 300, overhead_reserve = 150):
    system_tokens = count_tokens(system_prompt)
    user_tokens = count_tokens(user_message)
    
    history_budget = (total_budget - system_tokens - user_tokens - response_reserve - overhead_reserve)
    
    if history_budget < 0:
        raise ValueError("Not enough tokens for this request")
    
    selected_history = get_context_by_tokens(
        previous_messages,
        max_tokens=history_budget
    )

    # Construct final messages for OpenAI
    chat_history = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    chat_history.extend(selected_history)

    chat_history.append({
        "role": "user",
        "content": user_message
    })

    return chat_history

    



def get_context_by_tokens(messages, max_tokens=100):

    selected_messages = []
    used_tokens = 0

    # Group user and assistant messages into turns
    turns = []
    current_turn = []

    for msg in messages:

        if msg["role"] == "user":
            if current_turn:
                turns.append(current_turn)

            current_turn = [msg]

        elif msg["role"] == "assistant":
            if current_turn:
                current_turn.append(msg)

    if current_turn:
        turns.append(current_turn)

    # Select complete turns, newest first
    for turn in reversed(turns):

        turn_tokens = sum(
            count_tokens(msg["content"])
            for msg in turn
        )

        if used_tokens + turn_tokens > max_tokens:
            break

        selected_messages = turn + selected_messages
        used_tokens += turn_tokens

    return selected_messages

