import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o-mini")

text = "What is diabetes?"

tokens = encoding.encode(text)

print("Token IDs:", tokens)

for token in tokens:
    print(repr(encoding.decode([token])))