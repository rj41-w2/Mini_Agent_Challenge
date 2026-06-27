import os, sys, datetime
import google.generativeai as genai

def log_complaint(complaint_text: str) -> str:
    """Logs a negative complaint into the complaints file with a timestamp."""
    with open("complaints.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} - {complaint_text}\n")
    return "Complaint logged."

def read_complaints() -> str:
    """Reads the history of complaints and returns them."""
    if not os.path.exists("complaints.txt"):
        return "No complaints logged yet."
    with open("complaints.txt", "r") as f:
        lines = f.readlines()
    return f"Total complaints received: {len(lines)}\n" + "".join(lines)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("\n[ERROR] GEMINI_API_KEY set nahi hai! Pehle terminal mein key set karein.")
    print("Windows CMD: set GEMINI_API_KEY=your_key")
    print("PowerShell: $env:GEMINI_API_KEY=\"your_key\"\n")
    sys.exit(1)

genai.configure(api_key=api_key)

instruction = (
    "Analyze the user's input. "
    "If the user asks about the history of complaints, call read_complaints and provide a helpful summary to the user. "
    "Otherwise, determine the sentiment of the input. "
    "If NEGATIVE, first call log_complaint with the exact sentence, then output EXACTLY the word: NEGATIVE. "
    "If POSITIVE, output EXACTLY the word: POSITIVE."
)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    tools=[log_complaint, read_complaints],
    system_instruction=instruction
)
chat = model.start_chat(enable_automatic_function_calling=True)

while True:
    text = input("\nEnter a message (type 'exit' to stop): ")
    if text.strip().lower() == 'exit':
        break
        
    try:
        response = chat.send_message(text)
        out = response.text.strip()
        
        if out.upper() == "NEGATIVE":
            print("Bro, why so angry?")
        elif out.upper() == "POSITIVE":
            print("That's the spirit! Keep it positive.")
        else:
            print(out)
    except Exception as e:
        print(f"\n[ERROR] Request fail ho gayi. Wajah: {e}")
