'use client';

import { useState, useRef, useEffect } from 'react';

type Message = {
  role: 'user' | 'assistant';
  text: string;
  emotion?: string;
};

type HistoryItem = {
  id: number;
  timestamp: string;
  emotion: string;
  user_text: string;
};

export default function Home() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', text: "Hello! I'm your empathetic AI assistant. How are you feeling today?", emotion: "NEUTRAL" }
  ]);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;
    
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', text: data.reply, emotion: data.emotion }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', text: "Connection Error. Please try again.", emotion: "ERROR" }]);
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
        <header className="chat-header">
          <div>
            <h1>Sentiment Assistant</h1>
            <p className="subtitle">With Contextual Memory & Multi-Tools</p>
          </div>
          <button className="icon-btn" onClick={loadHistory} title="View Database History">
            🗄️ History
          </button>
        </header>

        <div className="chat-window">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-bubble ${msg.role}`}>
              {msg.role === 'assistant' && msg.emotion && msg.emotion !== "NEUTRAL" && (
                <span className="emotion-badge">{msg.emotion}</span>
              )}
              <p>{msg.text}</p>
            </div>
          ))}
          {loading && (
            <div className="chat-bubble assistant typing">
              <span className="dot"></span><span className="dot"></span><span className="dot"></span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="input-area" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Type your message here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>

      {showHistory && (
        <div className="history-modal">
          <div className="history-content">
            <button className="close-btn" onClick={() => setShowHistory(false)}>×</button>
            <h2 style={{ marginBottom: '20px' }}>Database Logs</h2>
            {history.length === 0 ? (
              <p>No history found.</p>
            ) : (
              history.map((item) => (
                <div key={item.id} className="history-item">
                  <span className="emotion-badge">{item.emotion}</span>
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
