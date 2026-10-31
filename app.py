
from flask import Flask, render_template, request, jsonify, stream_with_context, Response
import openai
from dotenv import load_dotenv
import os
import sqlite3
from prompts import MEDICAL_SYSTEM_PROMPT
import json
from context_manager import build_context

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
    welcome_message = "Welcome to MedAssist AI! How can I assist you with your health questions today?"
    
    return render_template('index.html', welcome_message=welcome_message)

# chat route
@app.route('/chat', methods=['POST'])
def chat():
    conn = None
    try:
        data = request.get_json(silent = True)
        
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON data"}), 400
        
        user_message = data.get("message")
        chat_id = data.get("chat_id")
        
        if not isinstance(user_message, str):
            return jsonify({"error": "Message must be a string"}), 400
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        if not chat_id:
            return jsonify({"error": "Chat ID is required"}), 400
        
        user_message = user_message.strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        if len(user_message) > 2000:
            return jsonify({
                "error": "Message cannot exceed 2000 characters"
            }), 400

        if not isinstance(chat_id, int) or isinstance(chat_id, bool) or chat_id <= 0:
            return jsonify({"error": "Valid Chat ID is required"}), 400
        
        # connect to db
        conn = get_db()
        cursor = conn.cursor()
        
        # check if convo exists
        cursor.execute(
            "select id from conversations where id = ?",
            (chat_id,)
        )
        
        if not cursor.fetchone():
            return jsonify({"error": "Chat not found"}), 404
        
        # get prev messages
        cursor.execute(
            "select role, content from messages where conversation_id = ? order by id",
            (chat_id,)
        )
        prev_messages = cursor.fetchall()
        
        # initialize the chat history
        chat_history = [
            {
                "role": "system",
                "content": MEDICAL_SYSTEM_PROMPT
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
            temperature=0.5,
            timeout = 30,
        )

        reply = response.choices[0].message.content
        
        if not reply or not reply.strip():
            raise ValueError("The AI could not generate a response.")
        
        reply = reply.strip()

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

        return jsonify({
            "reply": reply,
            "chat_id": chat_id
        })

    except openai.RateLimitError:
        return jsonify({
            "error": "The AI service is busy. Please try again shortly."
        }), 429

    except openai.APITimeoutError:
        return jsonify({
            "error": "The AI took too long to respond. Please try again."
        }), 504

    except openai.APIConnectionError:
        return jsonify({
            "error": "Unable to connect to the AI service. Please try again."
        }), 503

    except openai.APIStatusError:
        return jsonify({
            "error": "The AI service encountered an error."
        }), 502

    except ValueError:
        return jsonify({
            "error": "The AI could not generate a response."
        }), 502
        
    except Exception:
        app.logger.exception("Unexpected error occurred during chat processing.")
        return jsonify({
            "error": "An unexpected error occurred. Please try again."
        }), 500
    
    finally:
        if conn is not None:
            if conn.in_transaction:
                conn.rollback()
            conn.close()

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


# Stream a real conversation
@app.route("/chat-stream", methods=["POST"])
def chat_stream():

    data = request.get_json(silent=True)

    # Input guardrails
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    message = data.get("message")
    chat_id = data.get("chat_id")

    if not isinstance(message, str):
        return jsonify({"error": "Message must be text"}), 400

    message = message.strip()

    if not message or len(message) > 2000:
        return jsonify({"error": "Invalid message length"}), 400

    if type(chat_id) is not int or chat_id <= 0:
        return jsonify({"error": "Invalid chat ID"}), 400

    # Retrieve previous conversation
    conn = None

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM conversations WHERE id = ?",
            (chat_id,)
        )

        if not cursor.fetchone():
            return jsonify({"error": "Chat not found"}), 404

        cursor.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (chat_id,)
        )

        previous_messages = cursor.fetchall()

    except sqlite3.Error:
        app.logger.exception("Database read failed")
        return jsonify({"error": "Unable to load chat"}), 500

    finally:
        if conn is not None:
            conn.close()

    # Build chat history
    # Convert SQLite rows into dictionaries
    history = [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in previous_messages
    ]

    # Build context within token budget
    chat_history = build_context(
        system_prompt=MEDICAL_SYSTEM_PROMPT,
        previous_messages=history,
        user_message=message,
        total_budget=4000,
        response_reserve=300,
        overhead_reserve=200
    )

    for msg in previous_messages:
        chat_history.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    chat_history.append({
        "role": "user",
        "content": message
    })

    # Convert events to SSE format
    def send_event(event_type, content):
        payload = json.dumps({"content": content})
        return f"event: {event_type}\ndata: {payload}\n\n"

    # Generate and stream the AI response
    def generate():
        full_reply = ""

        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=chat_history,
                max_tokens=300,
                temperature=0.5,
                stream=True,
                timeout=30
            )

            for chunk in stream:
                if not chunk.choices:
                    continue

                text = chunk.choices[0].delta.content

                if text:
                    full_reply += text
                    yield send_event("chunk", text)

            if not full_reply.strip():
                raise ValueError("Empty AI response")

            # Save completed conversation
            db = None

            try:
                db = get_db()
                cursor = db.cursor()

                cursor.execute(
                    """
                    INSERT INTO messages
                    (conversation_id, role, content)
                    VALUES (?, ?, ?)
                    """,
                    (chat_id, "user", message)
                )

                cursor.execute(
                    """
                    INSERT INTO messages
                    (conversation_id, role, content)
                    VALUES (?, ?, ?)
                    """,
                    (chat_id, "assistant", full_reply)
                )

                if len(previous_messages) == 0:
                    cursor.execute(
                        """
                        UPDATE conversations
                        SET title = ?
                        WHERE id = ?
                        """,
                        (message[:40], chat_id)
                    )

                db.commit()

            except sqlite3.Error:
                if db is not None:
                    db.rollback()
                raise

            finally:
                if db is not None:
                    db.close()

            yield send_event("done", "complete")

        except Exception:
            app.logger.exception("Chat streaming failed")

            yield send_event(
                "error",
                "Unable to complete the response. Please try again."
            )

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# Temporary route to test Flask streaming
@app.route('/stream-test', methods=['GET'])
def stream_test():

    def generate():

        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": "Explain fever in 3 simple sentences."
                    }
                ],
                stream=True,
                timeout=30
            )

            for chunk in stream:
                if chunk.choices:
                    text = chunk.choices[0].delta.content

                    if text:
                        yield f"data: {text}\n\n"

            yield "event: done\ndata: complete\n\n"

        except openai.OpenAIError:
            app.logger.exception("Streaming API error")
            yield "event: error\ndata: AI service unavailable\n\n"

        except Exception:
            app.logger.exception("Unexpected streaming error")
            yield "event: error\ndata: Something went wrong\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# execute the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
