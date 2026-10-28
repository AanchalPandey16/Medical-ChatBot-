
from flask import Flask, render_template, request, jsonify
import openai
from dotenv import load_dotenv
import os
import sqlite3

# load the env variable
load_dotenv()
api_key = os.getenv("OPENAI_KEY")

client = openai.OpenAI(
    api_key=api_key
)

# initialize the Flask app
app = Flask(__name__)

# db to store the conversations and messages
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn



# create default route
@app.route('/')
def index():
    return render_template('index.html')

# chat route
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        chat_id = data.get("chat_id")
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        if not chat_id:
            return jsonify({"error": "Chat ID is required"}), 400
        
        # connect to db
        conn = get_db()
        cursor = conn.cursor()
        
        # check if convo exists
        cursor.execute(
            "select id from conversations where id = ?",
            (chat_id,)
        )
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Chat not found"}), 404
        
        # get prev msz
        cursor.execute(
            "select role, content from messages where conversation_id = ? order by id",
            (chat_id,)
        )
        prev_messages = cursor.fetchall()
        
        # initialize the chat history
        chat_history = [
            {
                "role": "system",
                "content": """
                You are a helpful medical assistant.
                Remember the conversation context.
                Provide clear and simple medical information.
                Ask relevant follow-up questions.
                Do not provide definitive diagnoses.
                """
            }
        ]
        
        for msg in prev_messages:
            chat_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # add user message to chat history
        chat_history.append({
            "role": "user",
            "content": user_message
        })

        # pass the prompt to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history,
            max_tokens=300,
            temperature=0.5
        )

        reply = response.choices[0].message.content.strip()
        
        

        # save user message to database
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (chat_id, "user", user_message)
        )

        # save bot response to database
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (chat_id, "assistant", reply)
        )

        # update chat title for first message
        if len(prev_messages) == 0:
            cursor.execute(
                "UPDATE conversations SET title = ? WHERE id = ?",
                (user_message[:40], chat_id)
            )

        # save the changes
        conn.commit()
        conn.close()

        return jsonify({
            "reply": reply,
            "chat_id": chat_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# get messages of a selected chat
@app.route('/chat/<int:chat_id>', methods=['GET'])
def get_chat_messages(chat_id):
    conn = get_db()
    cursor = conn.cursor()

    # check if chat exists
    cursor.execute(
        "SELECT id FROM conversations WHERE id = ?",
        (chat_id,)
    )

    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Chat not found"}), 404

    # get previous messages
    cursor.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id",
        (chat_id,)
    )

    messages = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify(messages)


@app.route('/new_chat', methods = ['POST'])
def new_chat():
    conn = get_db()
    cursor = conn.cursor()
    
    # create a new conversation
    cursor.execute("INSERT INTO conversations (title) VALUES (?)", ("New Chat",))
    
    conn.commit()
    chat_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"chat_id": chat_id, "message": "New chat created successfully."}), 201


# get all previous conversations
@app.route('/chats', methods=['GET'])
def get_chats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, created_at FROM conversations ORDER BY id DESC"
    )

    chats = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(chats)


# delete a selected chat
@app.route('/chat/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    conn = get_db()
    cursor = conn.cursor()

    # check if chat exists
    cursor.execute(
        "SELECT id FROM conversations WHERE id = ?",
        (chat_id,)
    )

    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Chat not found"}), 404

    # delete chat messages
    cursor.execute(
        "DELETE FROM messages WHERE conversation_id = ?",
        (chat_id,)
    )

    # delete conversation
    cursor.execute(
        "DELETE FROM conversations WHERE id = ?",
        (chat_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Chat deleted successfully"})


# execute the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
