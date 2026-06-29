import os, sys, datetime, sqlite3, json
from fastapi import FastAPI, HTTPException, Form, Response, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse
import contextvars

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "emotions_log.db")

# Context variable to keep track of the current user during a request
current_user = contextvars.ContextVar('current_user', default='global')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    timestamp TEXT,
                    emotion TEXT,
                    user_text TEXT
                 )''')
    conn.commit()
    conn.close()

def log_emotion_to_db(emotion: str, text: str) -> str:
    """Saves the user's emotion and exact sentence to the SQLite database.
    Use this tool whenever the user expresses an emotion in their sentence.
    """
    user_id = current_user.get()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (user_id, timestamp, emotion, user_text) VALUES (?, ?, ?, ?)", 
              (user_id, str(datetime.datetime.now()), emotion.upper(), text))
    conn.commit()
    conn.close()
    return "Log saved to database successfully."

def read_history_from_db() -> str:
    """Reads the current user's past conversational history and emotional complaints from the database.
    Use this tool if the user asks about their past complaints, history, or what they said before.
    """
    user_id = current_user.get()
    if not os.path.exists(DB_FILE):
        return "No history found."
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs WHERE user_id=? ORDER BY id ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return "No history found."
    
    history_str = "User's Past History:\n"
    for row in rows:
        history_str += f"[{row['timestamp']}] Emotion: {row['emotion']} | Text: {row['user_text']}\n"
    return history_str

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("\n[ERROR] GEMINI_API_KEY set nahi hai! Pehle terminal mein key set karein.")
    sys.exit(1)

genai.configure(api_key=api_key)
init_db()

instruction = (
    "You are an empathetic, highly intelligent AI Assistant with contextual memory. "
    "You remember everything in the current chat. "
    "1. If the user expresses an emotion, use 'log_emotion_to_db' to save it. Valid categories: POSITIVE, NEGATIVE, SAD, SARCASTIC, EXCITED, NEUTRAL. "
    "2. If the user asks about their past, use 'read_history_from_db' to retrieve it. "
    "3. You MUST ALWAYS respond ONLY IN ENGLISH. No matter what language the user speaks (Hindi, Urdu, Spanish, etc.), your REPLY MUST ALWAYS BE IN ENGLISH. "
    "CRITICAL INSTRUCTION: You MUST format your final response to the user EXACTLY in this format:\n\n"
    "EMOTION: [Detected Emotion or NEUTRAL]\n"
    "REPLY: [Your natural conversational response to the user IN ENGLISH ONLY]"
)

# CHANGED MODEL TO gemini-1.5-flash FOR HIGHER RATE LIMITS
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    tools=[log_emotion_to_db, read_history_from_db],
    system_instruction=instruction
)

# Global dictionary to hold user sessions
chat_sessions = {}

def get_session(user_id: str):
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(enable_automatic_function_calling=True)
    return chat_sessions[user_id]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        user_id = request.user_id
        current_user.set(user_id)
        session = get_session(user_id)
        
        response = session.send_message(request.message)
        text = response.text.strip()
        
        emotion = "NEUTRAL"
        reply = text
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("EMOTION:"):
                emotion = line.replace("EMOTION:", "").strip()
            elif line.startswith("REPLY:"):
                reply = "\n".join(lines[i:]).replace("REPLY:", "").strip()
                break
                
        if "EMOTION:" not in text and "REPLY:" not in text:
            reply = text
            
        return {"reply": reply, "emotion": emotion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/whatsapp")
async def whatsapp(Body: str = Form(...), From: str = Form(...)):
    try:
        user_id = From
        current_user.set(user_id)
        session = get_session(user_id)
        
        response = session.send_message(Body)
        text = response.text.strip()
        
        reply = text
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("REPLY:"):
                reply = "\n".join(lines[i:]).replace("REPLY:", "").strip()
                break
                
        if "EMOTION:" not in text and "REPLY:" not in text:
            reply = text

        twiml = MessagingResponse()
        twiml.message(reply)
        return Response(content=str(twiml), media_type="application/xml")
    except Exception as e:
        twiml = MessagingResponse()
        twiml.message("Sorry, I encountered an error: " + str(e))
        return Response(content=str(twiml), media_type="application/xml")

@app.get("/api/history")
async def history(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs WHERE user_id=? ORDER BY id DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return {"history": [dict(row) for row in rows]}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend", "out")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
elif os.path.exists("frontend/out"):
    app.mount("/", StaticFiles(directory="frontend/out", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
