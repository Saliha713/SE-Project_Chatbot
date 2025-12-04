import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";
import { v4 as uuidv4 } from "uuid"; // for generating session IDs
import ReactMarkdown from "react-markdown"; // Added for Markdown rendering

function App() {
  const [messages, setMessages] = useState([
    { from: "bot", text: "Hello! I'm your Airline Assistant — ask me anything about flights, baggage, or policies." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const backendBase = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

  // Generate session ID for memory
  const [sessionId] = useState(() => uuidv4());

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendQuery(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;

    setMessages((m) => [...m, { from: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${backendBase}/query`, {
        query: text,
        top_k: 4,
        session_id: sessionId,
      });

      // Add bot response
      setMessages((m) => [
        ...m,
        { from: "bot", text: res.data.answer },
      ]);

      // Add sources as separate message
      if (res.data.sources && res.data.sources.length > 0) {
        const sourcesText = res.data.sources.map((s) => `Page ${s.page}`).join(", ");
        setMessages((m) => [...m, { from: "bot", text: `**Sources:** ${sourcesText}` }]);
      }
    } catch (err) {
      console.error(err);
      setMessages((m) => [
        ...m,
        { from: "bot", text: `Query failed: ${err?.response?.data?.detail || err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <h1>Airline Chatbot ✈️</h1>
      <div className="chat-container">
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.from}`}>
              <div className="text">
                {/* Use ReactMarkdown to render bot messages */}
                <ReactMarkdown>{m.text}</ReactMarkdown>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef}></div>
        </div>

        <form className="controls" onSubmit={sendQuery}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about flights, baggage, refunds..."
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Thinking..." : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
