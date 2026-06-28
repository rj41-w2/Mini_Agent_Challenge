import os, sys, datetime, sqlite3
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, emotion, user_text) VALUES (?, ?, ?)", 
              (str(datetime.datetime.now()), emotion.upper(), text))
    conn.commit()
    conn.close()
    return "Log saved to database successfully."

def read_history_from_db() -> list:
    if not os.path.exists(DB_FILE):
        return []
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("\n[ERROR] GEMINI_API_KEY set nahi hai! Pehle terminal mein key set karein.")
    sys.exit(1)

genai.configure(api_key=api_key)
init_db()

instruction = (
    "Analyze the user's input. "
    "Determine the sentiment/emotion of the input. Valid categories: POSITIVE, NEGATIVE, SAD, SARCASTIC, EXCITED, NEUTRAL. "
    "You MUST first call log_emotion_to_db with the detected emotion and the exact user sentence. "
    "Then output EXACTLY the emotion word (e.g., NEGATIVE, POSITIVE, SAD, etc.)."
)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    tools=[log_emotion_to_db],
    system_instruction=instruction
)

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

responses = {
    "NEGATIVE": "Bro, why so angry?",
    "POSITIVE": "That's the spirit! Keep it positive.",
    "SAD": "Cheer up, everything will be alright!",
    "SARCASTIC": "Wow, so funny. Not.",
    "EXCITED": "Whoa, calm down, take a deep breath!",
    "NEUTRAL": "Okay, got it."
}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        chat_session = model.start_chat(enable_automatic_function_calling=True)
        response = chat_session.send_message(request.message)
        out = response.text.strip().upper()
        
        reply = out
        for emotion, res in responses.items():
            if emotion in out:
                reply = res
                break
                
        return {"reply": reply, "emotion": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def history():
    return {"history": read_history_from_db()}

# Serve Next.js static files
if os.path.exists("frontend/out"):
    app.mount("/", StaticFiles(directory="frontend/out", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
