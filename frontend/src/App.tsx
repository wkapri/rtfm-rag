import { useState } from "react";
import StatsPanel from "./StatsPanel";

interface Source {
  filename: string;
  page: number;
}

interface RetrievedChunk {
  rank: number;
  filename: string;
  page: number;
  preview: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  queryLogId?: string;
  feedback?: 1 | -1;
  refused?: boolean;
  retrievalLatencyMs?: number;
  embedLatencyMs?: number;
  searchLatencyMs?: number;
  generationLatencyMs?: number;
  retrievedChunks?: RetrievedChunk[];
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showStats, setShowStats] = useState(false);

  async function sendMessage() {
    if (!input.trim()) return;
    const question = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question }),
      });
      const data: {
        answer: string;
        sources: Source[];
        query_log_id: string;
        refused: boolean;
        retrieval_latency_ms: number;
        embed_latency_ms: number;
        search_latency_ms: number;
        generation_latency_ms: number;
        retrieved_chunks: RetrievedChunk[];
      } = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          queryLogId: data.query_log_id,
          refused: data.refused,
          retrievalLatencyMs: data.retrieval_latency_ms,
          embedLatencyMs: data.embed_latency_ms,
          searchLatencyMs: data.search_latency_ms,
          generationLatencyMs: data.generation_latency_ms,
          retrievedChunks: data.retrieved_chunks,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function sendFeedback(index: number, feedback: 1 | -1) {
    const message = messages[index];
    if (!message.queryLogId) return;
    setMessages((prev) => prev.map((m, i) => (i === index ? { ...m, feedback } : m)));
    await fetch(`/api/feedback/${message.queryLogId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback }),
    });
  }

  return (
    <div style={{ maxWidth: 720, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h1>rag1 — manual chat</h1>
        <button onClick={() => setShowStats((s) => !s)}>
          {showStats ? "Hide stats" : "Show stats"}
        </button>
      </div>

      {showStats && <StatsPanel />}

      <div style={{ minHeight: 300, border: "1px solid #ccc", padding: 12, marginBottom: 12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 12 }}>
            <p style={{ margin: 0 }}>
              <strong>{m.role === "user" ? "You" : "Assistant"}:</strong> {m.content}
              {m.refused && (
                <span style={{ marginLeft: 6, fontSize: "0.8em", color: "#a55" }}>(refused)</span>
              )}
            </p>

            {m.sources && m.sources.length > 0 && (
              <details style={{ marginTop: 4, fontSize: "0.9em", color: "#555" }}>
                <summary>Sources ({m.sources.length})</summary>
                <ul style={{ margin: "4px 0" }}>
                  {m.sources.map((s, j) => (
                    <li key={j}>
                      {s.filename}, page {s.page}
                    </li>
                  ))}
                </ul>
              </details>
            )}

            {m.retrievedChunks && (
              <details style={{ marginTop: 4, fontSize: "0.85em", color: "#555" }}>
                <summary>
                  Details (embed {m.embedLatencyMs}ms + search {m.searchLatencyMs}ms = retrieval{" "}
                  {m.retrievalLatencyMs}ms, generation {m.generationLatencyMs}ms)
                </summary>
                <ul style={{ margin: "4px 0", paddingLeft: 18 }}>
                  {m.retrievedChunks.map((c) => (
                    <li key={c.rank}>
                      #{c.rank + 1} — {c.filename} p.{c.page}: <em>{c.preview}…</em>
                    </li>
                  ))}
                </ul>
              </details>
            )}

            {m.role === "assistant" && m.queryLogId && (
              <div style={{ marginTop: 4 }}>
                <button
                  onClick={() => sendFeedback(i, 1)}
                  style={{ opacity: m.feedback === 1 ? 1 : 0.4, marginRight: 4 }}
                  aria-label="Thumbs up"
                >
                  👍
                </button>
                <button
                  onClick={() => sendFeedback(i, -1)}
                  style={{ opacity: m.feedback === -1 ? 1 : 0.4 }}
                  aria-label="Thumbs down"
                >
                  👎
                </button>
              </div>
            )}
          </div>
        ))}
        {loading && <p>Thinking…</p>}
      </div>
      <input
        style={{ width: "80%" }}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        placeholder="Ask about your manuals…"
      />
      <button onClick={sendMessage} disabled={loading}>
        Send
      </button>
    </div>
  );
}
