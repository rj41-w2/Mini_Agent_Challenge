'use client';

import { useState } from 'react';

type ChatResponse = {
  reply: string;
  emotion: string;
};

type HistoryItem = {
  id: number;
  timestamp: string;
  emotion: string;
  user_text: string;
};

export default function Home() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const handleSubmit = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setResponse(null);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      console.error(error);
      setResponse({ reply: "Connection Error. Please try again.", emotion: "ERROR" });
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      setHistory(data.history);
      setShowHistory(true);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <main>
      <div className="app-container">
        <h1>Sentiment Sorter</h1>
        <p className="subtitle">Your AI companion that understands your emotions</p>

        <div className="chat-box">
          <textarea
            placeholder="Type your message here..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={loading}
          />

          <div className="button-group">
            <button onClick={handleSubmit} disabled={loading}>
              {loading ? 'Analyzing...' : 'Send Message'}
            </button>
            <button className="secondary" onClick={loadHistory}>
              View History
            </button>
          </div>
        </div>

        {response && (
          <div className="response-card">
            <span className="emotion-tag">{response.emotion}</span>
            <p>{response.reply}</p>
          </div>
        )}
      </div>

      {showHistory && (
        <div className="history-modal">
          <div className="history-content">
            <button className="close-btn" onClick={() => setShowHistory(false)}>×</button>
            <h2 style={{ marginBottom: '20px' }}>Conversation History</h2>
            {history.length === 0 ? (
              <p>No history found.</p>
            ) : (
              history.map((item) => (
                <div key={item.id} className="history-item">
                  <span className="emotion-tag">{item.emotion}</span>
                  <p><strong>You:</strong> {item.user_text}</p>
                  <p className="text-muted">{new Date(item.timestamp).toLocaleString()}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </main>
  );
}
