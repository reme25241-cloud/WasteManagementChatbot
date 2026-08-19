# EcoBot - Waste Management Chatbot

EcoBot is a memory-based AI chatbot for **waste management** built using **Flask, SQLite, Bootstrap 5, Ollama, and Llama 3.2**.

The chatbot helps users understand different types of waste, recycling methods, disposal practices, recommendations, and ways to reduce waste.

The application also maintains conversation history using SQLite, allowing the chatbot to remember previous messages during the conversation.

---

## Features

- AI-powered waste management chatbot
- Uses local `llama3.2:latest` through Ollama
- Memory-based conversation
- SQLite database for storing chat history
- JSON-based waste management knowledge base
- Waste description
- Waste type classification
- Recycling information
- Disposal recommendations
- Reuse suggestions
- Waste reduction suggestions
- Responsive Bootstrap 5 webpage
- Floating chatbot icon
- Bootstrap modal chatbot interface
- Clear conversation memory
- Flask backend
- No custom CSS
- No custom JavaScript

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Flask | Web framework |
| Ollama | Local LLM runtime |
| Llama 3.2 | AI language model |
| SQLite | Conversation memory |
| JSON | Waste knowledge base |
| Bootstrap 5 | UI styling and interactions |
| Gunicorn | Production WSGI server |

---

## Project Structure

```text
session3/
│
├── app.py
├── data.json
├── db.sqlite
├── requirements.txt
├── README.md
│
└── templates/
    └── index.html
