# Sentiment Sorter / AI Assistant

Welcome to the **Sentiment Sorter**, an empathetic, intelligent AI Assistant designed with contextual memory and emotion tracking. Built for the Mini Agent Challenge, this full-stack application utilizes the latest web and AI technologies.

## 🚀 Features

- **Empathetic AI Assistant:** Driven by the **Gemini 2.5 Flash** model to provide thoughtful and contextual responses in English.
- **Emotion Tracking & Contextual Memory:** The AI automatically detects when you express emotions (POSITIVE, NEGATIVE, SAD, SARCASTIC, EXCITED, NEUTRAL) and logs them into a local SQLite database using **Gemini API Function Calling**. It remembers your past conversational history!
- **Multi-Platform Support:** 
  - **Web UI:** A modern, responsive user interface built with Next.js 16 and Tailwind CSS.
  - **WhatsApp Integration:** Interact with the AI through WhatsApp via a Twilio Webhook.
- **FastAPI Backend:** A robust Python backend handling API requests, Twilio webhook integration, database operations, and serving static frontend files.

## 🛠️ Technology Stack

- **Backend:** Python, FastAPI, SQLite, Google Generative AI (Gemini), Twilio (for WhatsApp)
- **Frontend:** Next.js 16 (React 19), Tailwind CSS, TypeScript

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your machine:
- **Python 3.8+**
- **Node.js (v18 or higher)**
- **npm** (comes with Node.js)
- A **Gemini API Key** from Google AI Studio.
- (Optional) A Twilio account if you want to use the WhatsApp feature.

---

## 💻 Setup Instructions & Running Locally

Follow these steps to get the project up and running on your local machine.

### 1. Clone or Navigate to the Project Directory
```bash
cd /path/to/Mini_Agent_Challenge
```

### 2. Configure Environment Variables
You must set your Gemini API key before starting the backend server.
**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```
**Mac/Linux:**
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

### 3. Backend Setup
Navigate to the backend directory and install the required Python dependencies.
```bash
cd backend
pip install -r requirements.txt
```

Run the FastAPI backend server:
```bash
python sorter.py
```
> The backend server will start on `http://localhost:7860`. It automatically creates an SQLite database (`emotions_log.db`) for tracking user emotions and history.

### 4. Frontend Setup
Open a **new terminal window**, navigate to the frontend directory, and install the dependencies.
```bash
cd frontend
npm install
```

Start the Next.js development server:
```bash
npm run dev
```
> The frontend will typically run on `http://localhost:3000`. Open this URL in your browser to interact with the Sentiment Sorter!

*(Alternatively, you can run `npm run build` in the frontend directory to generate a static export in the `out/` folder. The FastAPI backend is configured to automatically serve this static folder at `http://localhost:7860/` if it exists).*

---

## 📱 WhatsApp Integration (Twilio)

The backend provides an endpoint specifically for Twilio WhatsApp webhooks.
1. Set up a Twilio sandbox for WhatsApp.
2. Expose your local server to the internet using a tool like [ngrok](https://ngrok.com/).
   ```bash
   ngrok http 7860
   ```
3. Configure your Twilio WhatsApp Sandbox Webhook URL to point to `https://<your-ngrok-url>/api/whatsapp`.
4. Send a message to your Twilio Sandbox number, and the Gemini AI will respond!

---

## 📂 Project Structure

```text
Mini_Agent_Challenge/
├── backend/
│   ├── sorter.py          # Main FastAPI application & Gemini setup
│   ├── requirements.txt   # Python dependencies
│   └── emotions_log.db    # SQLite database (generated at runtime)
└── frontend/
    ├── package.json       # Node dependencies and scripts
    ├── src/               # Next.js app source code
    └── ...                # Other Next.js configuration files
```
