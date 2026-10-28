"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import axios from "axios";
import Link from "next/link";

export default function ChatDocumentPage() {
  const { id } = useParams();
  const router = useRouter();

  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = { role: "user", content: question };
    setChatHistory([...chatHistory, userMessage]);
    setQuestion("");
    setError("");
    setAsking(true);

    try {
      const response = await axios.post("http://localhost:5000/api/documents/chat", {
        question: userMessage.content,
        document_id: parseInt(id)
      }, {
        withCredentials: true
      });

      if (response.data.success) {
        const aiMessage = { 
          role: "ai", 
          content: response.data.answer,
          sources: response.data.sources 
        };
        setChatHistory(prev => [...prev, aiMessage]);
      } else {
        setError(response.data.message || "Failed to get answer");
      }
    } catch (err) {
      setError(err.response?.data?.message || "Failed to get answer");
    } finally {
      setAsking(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Chat with Document #{id}</h1>
        <button className="btn-secondary" onClick={() => router.push("/documents")}>
          Back to Documents
        </button>
      </div>

      <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '65vh' }}>
        <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem', padding: '1rem', border: '1px solid var(--border)', borderRadius: '6px' }}>
          {chatHistory.length === 0 ? (
            <p className="text-gray-500 text-center mt-10">Ask a question about this document to start chatting!</p>
          ) : (
            chatHistory.map((msg, idx) => (
              <div key={idx} style={{ 
                marginBottom: '1rem', 
                padding: '1rem', 
                borderRadius: '6px',
                backgroundColor: msg.role === 'user' ? 'var(--bg-secondary)' : 'var(--bg-primary)',
                border: msg.role === 'ai' ? '1px solid var(--border)' : 'none'
              }}>
                <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong>
                <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>{msg.content}</p>
                
                {msg.sources && msg.sources.length > 0 && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    <em>Sources used: {msg.sources.length} chunk(s) from document.</em>
                  </div>
                )}
              </div>
            ))
          )}
          {asking && <p className="text-gray-500 text-sm mt-2">Thinking...</p>}
        </div>

        {error && <p className="error-text mb-2">{error}</p>}

        <form onSubmit={handleAsk} style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            className="input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            disabled={asking}
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn-primary" disabled={asking || !question.trim()}>
            Ask
          </button>
        </form>
      </div>
    </div>
  );
}
