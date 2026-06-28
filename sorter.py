import os, sys, datetime, sqlite3, json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

DB_FILE = "emotions_log.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, emotion, user_text) VALUES (?, ?, ?)", 
              (str(datetime.datetime.now()), emotion.upper(), text))
    conn.commit()
    conn.close()
    return "Log saved to database successfully."

def read_history_from_db() -> str:
    """Reads the user's past conversational history and emotional complaints from the database.
    Use this tool if the user asks about their past complaints, history, or what they said before.
    """
    if not os.path.exists(DB_FILE):
        return "No history found."
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id ASC")
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

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    tools=[log_emotion_to_db, read_history_from_db],
    system_instruction=instruction
)

# Global chat session to maintain contextual memory across requests
chat_session = model.start_chat(enable_automatic_function_calling=True)

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

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        response = chat_session.send_message(request.message)
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

@app.get("/api/history")
async def history():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return {"history": [dict(row) for row in rows]}

if os.path.exists("frontend/out"):
    app.mount("/", StaticFiles(directory="frontend/out", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
