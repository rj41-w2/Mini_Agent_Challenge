# Skill: The Sentiment Sorter

## Intent
Analyze user text input and determine its emotional tone.

## Rules
1. Accept a single sentence input from the user.
2. Send the text to an LLM API with a strict system prompt.
3. The LLM output MUST be exactly one word: POSITIVE or NEGATIVE.
4. If the captured word is NEGATIVE, trigger a sympathetic print response.
5. AUTONOMOUS ACTION: If the sentiment is NEGATIVE, do not just print a message. You MUST autonomously## Available Tools (Multi-User Aware)

1. `log_emotion_to_db`: Logs an emotion (POSITIVE, NEGATIVE, SAD, SARCASTIC, EXCITED, NEUTRAL) and the user's sentence to an SQLite database (`backend/emotions_log.db`). It automatically links the log to the specific `user_id`.
2. `read_history_from_db`: Retrieves the private history of the current `user_id` from the database.

## System Details
- **Architecture**: Monorepo (Next.js frontend, FastAPI backend)
- **Database**: SQLite (`backend/emotions_log.db`)
- **Memory**: Contextual memory maintained per-user using `chat_sessions` dictionary and `contextvars`.
- **Model**: `gemini-1.5-flash` (used for higher rate limits).
- **Language**: English Only responses.
- **WhatsApp**: Integrated via Twilio API (`/api/whatsapp`).e output.