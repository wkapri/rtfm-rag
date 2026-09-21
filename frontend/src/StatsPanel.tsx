import { useEffect, useState } from "react";
import { CloseIcon } from "./Icons";

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

interface Props {
  onClose: () => void;
}

export default function StatsPanel({ onClose }: Props) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [logs, setLogs] = useState<LogRow[]>([]);
  const [error, setError] = useState(false);

  async function refresh() {
    try {
      const [statsRes, logsRes] = await Promise.all([fetch("/api/stats"), fetch("/api/logs?limit=10")]);
      if (!statsRes.ok || !logsRes.ok) throw new Error("request failed");
      setStats(await statsRes.json());
      setLogs(await logsRes.json());
      setError(false);
    } catch {
      setError(true);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer">
        <div className="drawer-header">
          <h2>Stats</h2>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <button className="refresh-button" onClick={refresh}>
              Refresh
            </button>
            <button className="icon-button" onClick={onClose} aria-label="Close">
              <CloseIcon size={16} />
            </button>
          </div>
        </div>

        <div className="drawer-body">
          {error && (
            <p style={{ color: "var(--danger)", fontSize: 13, marginTop: 0 }}>
              Couldn't reach the backend. Is it running?
            </p>
          )}
          {stats && (
            <div className="stat-grid">
              <StatCard label="Total queries" value={String(stats.total_queries)} />
              <StatCard label="Refusal rate" value={fmtPct(stats.refusal_rate)} />
              <StatCard label="Avg retrieval" value={fmtMs(stats.avg_retrieval_latency_ms)} />
              <StatCard label="Avg generation" value={fmtMs(stats.avg_generation_latency_ms)} />
              <StatCard
                label="Feedback"
                value={`👍 ${stats.thumbs_up}  👎 ${stats.thumbs_down}`}
                sub={`${stats.feedback_count} of ${stats.total_queries} rated`}
              />
            </div>
          )}

          <p className="section-label">Recent queries</p>
          <div className="log-list">
            {logs.length === 0 && <p style={{ color: "var(--text-faint)", fontSize: 13 }}>No queries yet.</p>}
            {logs.map((log) => (
              <div className="log-row" key={log.id}>
                <p className="log-row-question">{log.question}</p>
                <div className="log-row-meta">
                  <span>retrieval {log.retrieval_latency_ms}ms</span>
                  <span>gen {log.generation_latency_ms}ms</span>
                  {log.refused && <span style={{ color: "var(--danger)" }}>refused</span>}
                  {log.feedback === 1 && <span>👍</span>}
                  {log.feedback === -1 && <span>👎</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="stat-card">
      <p className="stat-card-label">{label}</p>
      <p className="stat-card-value">{value}</p>
      {sub && <p className="stat-card-label" style={{ marginTop: 4, textTransform: "none" }}>{sub}</p>}
    </div>
  );
}

function fmtMs(ms: number | null): string {
  return ms === null ? "—" : `${ms}ms`;
}

function fmtPct(rate: number | null): string {
  return rate === null ? "—" : `${Math.round(rate * 100)}%`;
}
