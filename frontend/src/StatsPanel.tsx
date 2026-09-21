import { useEffect, useState } from "react";

interface Stats {
  total_queries: number;
  avg_retrieval_latency_ms: number | null;
  avg_generation_latency_ms: number | null;
  refusal_rate: number | null;
  thumbs_up: number;
  thumbs_down: number;
  feedback_count: number;
}

interface LogRow {
  id: string;
  question: string;
  refused: boolean;
  retrieval_latency_ms: number;
  generation_latency_ms: number;
  feedback: number | null;
  created_at: string;
}

export default function StatsPanel() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [logs, setLogs] = useState<LogRow[]>([]);

  async function refresh() {
    const [statsRes, logsRes] = await Promise.all([
      fetch("/api/stats"),
      fetch("/api/logs?limit=10"),
    ]);
    setStats(await statsRes.json());
    setLogs(await logsRes.json());
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div style={{ border: "1px solid #ccc", padding: 12, marginBottom: 12, fontSize: "0.9em" }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <strong>Stats</strong>
        <button onClick={refresh}>Refresh</button>
      </div>

      {stats && (
        <table style={{ width: "100%", marginTop: 8, borderCollapse: "collapse" }}>
          <tbody>
            <Row label="Total queries" value={stats.total_queries} />
            <Row label="Avg retrieval latency" value={fmtMs(stats.avg_retrieval_latency_ms)} />
            <Row label="Avg generation latency" value={fmtMs(stats.avg_generation_latency_ms)} />
            <Row label="Refusal rate" value={fmtPct(stats.refusal_rate)} />
            <Row
              label="Feedback"
              value={`👍 ${stats.thumbs_up} / 👎 ${stats.thumbs_down} (${stats.feedback_count} of ${stats.total_queries} rated)`}
            />
          </tbody>
        </table>
      )}

      <details style={{ marginTop: 8 }}>
        <summary>Recent queries ({logs.length})</summary>
        <table style={{ width: "100%", marginTop: 4, borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
              <th>Question</th>
              <th>Refused</th>
              <th>Retrieval</th>
              <th>Generation</th>
              <th>Feedback</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} style={{ borderBottom: "1px solid #eee" }}>
                <td>{log.question}</td>
                <td>{log.refused ? "yes" : ""}</td>
                <td>{log.retrieval_latency_ms}ms</td>
                <td>{log.generation_latency_ms}ms</td>
                <td>{log.feedback === 1 ? "👍" : log.feedback === -1 ? "👎" : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <tr>
      <td style={{ color: "#555", paddingRight: 12 }}>{label}</td>
      <td>{value}</td>
    </tr>
  );
}

function fmtMs(ms: number | null): string {
  return ms === null ? "—" : `${ms}ms`;
}

function fmtPct(rate: number | null): string {
  return rate === null ? "—" : `${Math.round(rate * 100)}%`;
}
