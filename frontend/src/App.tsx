import { useState } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

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
      const text = await response.text();
      setMessages((prev) => [...prev, { role: "assistant", content: text }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>rag1 — manual chat</h1>
      <div style={{ minHeight: 300, border: "1px solid #ccc", padding: 12, marginBottom: 12 }}>
        {messages.map((m, i) => (
          <p key={i}>
            <strong>{m.role === "user" ? "You" : "Assistant"}:</strong> {m.content}
          </p>
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
