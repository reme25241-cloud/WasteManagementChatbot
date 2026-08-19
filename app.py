from flask import Flask, render_template, request
import sqlite3
import json
import requests
from datetime import datetime

app = Flask(__name__)

DATABASE = "db.sqlite"
DATA_FILE = "data.json"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:latest"


# --------------------------------------------------
# Database
# --------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# Waste Management Knowledge
# --------------------------------------------------

def load_waste_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


# --------------------------------------------------
# Memory
# --------------------------------------------------

def save_message(role, message):
    conn = get_db()

    conn.execute(
        """
        INSERT INTO messages (role, message, created_at)
        VALUES (?, ?, ?)
        """,
        (
            role,
            message,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()
    conn.close()


def get_memory(limit=12):
    conn = get_db()

    rows = conn.execute(
        """
        SELECT role, message
        FROM messages
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    conn.close()

    # Reverse so oldest message comes first
    return list(reversed(rows))


def clear_memory():
    conn = get_db()

    conn.execute("DELETE FROM messages")

    conn.commit()
    conn.close()


# --------------------------------------------------
# Ollama
# --------------------------------------------------

def ask_ollama(user_message):

    waste_data = load_waste_data()
    memory = get_memory()

    knowledge = json.dumps(
        waste_data,
        indent=2,
        ensure_ascii=False
    )

    system_prompt = f"""
You are EcoBot, an intelligent Waste Management Assistant.

Your job is to help users understand waste management.

You provide information about:

1. Waste description
2. Waste type
3. Whether it can be recycled
4. How to recycle it
5. Disposal methods
6. Recommendations
7. Suggestions for reducing waste
8. Reuse ideas
9. Composting when appropriate
10. Environmental impact

Use the following waste-management knowledge base:

{knowledge}

IMPORTANT RULES:

- Give practical and easy-to-understand answers.
- If the user mentions a waste item, identify its likely waste type.
- Explain whether it is recyclable.
- Explain how it should be disposed of.
- Give recommendations and suggestions.
- Encourage reuse and recycling when appropriate.
- Do not claim something is recyclable if the knowledge base does not support it.
- If local recycling rules may differ, clearly mention that users should check their local waste collection rules.
- Do not invent dangerous disposal methods.
- Maintain conversation context using the previous messages.
- Keep answers reasonably concise.

You are a helpful waste-management chatbot called EcoBot.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Add previous conversation memory
    for item in memory:
        messages.append({
            "role": item["role"],
            "content": item["message"]
        })

    # Add current question
    messages.append({
        "role": "user",
        "content": user_message
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        answer = result["message"]["content"]

        return answer

    except requests.exceptions.ConnectionError:

        return (
            "I cannot connect to Ollama. "
            "Please make sure Ollama is running and "
            "llama3.2:latest is available."
        )

    except requests.exceptions.Timeout:

        return (
            "The AI model took too long to respond. "
            "Please try again."
        )

    except Exception as e:

        return f"Sorry, an error occurred: {str(e)}"


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        user_message = request.form.get(
            "message",
            ""
        ).strip()

        if user_message:

            # Save user message
            save_message(
                "user",
                user_message
            )

            # Generate AI response
            answer = ask_ollama(
                user_message
            )

            # Save chatbot response
            save_message(
                "assistant",
                answer
            )

    memory = get_memory()

    return render_template(
        "index.html",
        memory=memory
    )


# --------------------------------------------------
# Clear Chat Memory
# --------------------------------------------------

@app.route("/clear", methods=["POST"])
def clear():

    clear_memory()

    return render_template(
        "index.html",
        memory=[]
    )


# --------------------------------------------------
# Run Application
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )