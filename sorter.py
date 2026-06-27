import os, datetime
import google.generativeai as genai

def log_complaint(t):
    with open("complaints.txt", "a") as f: f.write(f"{datetime.datetime.now()} - {t}\n")

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
while True:
    text = input("Enter a sentence (type 'exit' to stop): ")
    if text.strip().lower() == 'exit': break
    response = model.generate_content(f"Tell the sentiment of this text: POSITIVE or NEGATIVE. Return only one word.\n{text}")
    if "NEGATIVE" in response.text.strip().upper():
        print("Bro, why so angry?")
        log_complaint(text)
