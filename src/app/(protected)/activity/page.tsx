"use client";

import { useCallback, useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";

// Local header so this client page has no import into the server-component app-shell
// module (that cross-boundary import makes the Turbopack production build drop the route).
function PageHead({ title, description }: { title: string; description: string }) {
  return <div className="page-head"><div><h1>{title}</h1><p>{description}</p></div><div className="safety">Human-controlled research only</div></div>;
}

type Run = {
  id: string; programme_name: string; status: string; mode: string;
  targets_total: number; targets_done: number; findings_total: number;
  crit: number; high: number; med: number; low: number; info: number;
  summary: string; started_at: string; finished_at: string | null;
};
type Event = { id: string; step_no: number; title: string; detail: string; state: string; created_at: string };

const STATE_ICON: Record<string, string> = { active: "", done: "✓", info: "•", warn: "!" };

export default function ActivityPage() {
  const supabase = createClient();
  const [runs, setRuns] = useState<Run[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(async () => {
    const { data: runData } = await supabase.from("scan_runs").select("*").order("started_at", { ascending: false }).limit(15);
    const list = (runData || []) as Run[];
    setRuns(list);
    const runId = selected && list.some((r) => r.id === selected) ? selected : list[0]?.id ?? null;
    if (runId !== selected) setSelected(runId);
    if (runId) {
      const { data: evData } = await supabase.from("scan_events").select("*").eq("run_id", runId).order("created_at", { ascending: true }).order("step_no", { ascending: true });
      setEvents((evData || []) as Event[]);
    } else {
      setEvents([]);
    }
    setLoaded(true);
  }, [supabase, selected]);

  useEffect(() => {
    load();
    const t = setInterval(load, 2500); // live follow-along
    return () => clearInterval(t);
  }, [load]);

  const run = runs.find((r) => r.id === selected) || null;
  const running = run?.status === "running";

  return (
    <>
      <PageHead title="Scan Activity" description="Watch a scan work through the steps, live, in plain English" />

      {!loaded ? (
        <div className="card">Loading…</div>
      ) : !run ? (
        <div className="empty">No scans have run yet. When you start a scan, this page shows exactly what it is doing — step by step — as it happens.</div>
      ) : (
        <>
          <section className="card">
            <div className="record-top">
              <div>
                <h2 style={{ marginBottom: 4 }}>{run.programme_name || "Scan"}</h2>
                <span className="meta">{run.mode === "monitor" ? "Monitoring pass" : "Full scan"} · started {new Date(run.started_at).toLocaleString("en-GB")}</span>
              </div>
              <span className={`badge ${run.status === "running" ? "high" : run.status === "completed" ? "verified" : "medium"}`}>
                {running ? "Running…" : run.status === "completed" ? "Completed" : run.status}
              </span>
            </div>

            <div className="bar-row" style={{ marginTop: 12 }}>
              <span>Targets checked</span>
              <span className="bar"><span style={{ width: `${run.targets_total ? (run.targets_done / run.targets_total) * 100 : 0}%` }} /></span>
              <strong>{run.targets_done}/{run.targets_total}</strong>
            </div>

            <div className="grid metrics" style={{ marginTop: 12 }}>
              <Count label="Critical" value={run.crit} tone="#c0392b" />
              <Count label="High" value={run.high} tone="#e67e22" />
              <Count label="Medium" value={run.med} tone="#c99700" />
              <Count label="Low" value={run.low} tone="#2d7d54" />
            </div>

            {run.summary && <p style={{ marginTop: 12 }}>{run.summary}</p>}
            {running && <p className="meta" style={{ marginTop: 8 }}>This refreshes on its own — leave it open and watch it work.</p>}
          </section>

          <section className="card" style={{ marginTop: 16 }}>
            <h2>What it's doing</h2>
            <ol className="steps">
              {events.map((e) => (
                <li key={e.id} className={`step ${e.state}`}>
                  <span className="step-mark" aria-hidden>{e.state === "active" ? <span className="pulse" /> : STATE_ICON[e.state] || "•"}</span>
                  <div>
                    <strong>{e.title}</strong>
                    {e.detail && <div className="meta">{e.detail}</div>}
                  </div>
                </li>
              ))}
              {!events.length && <li className="meta">Waiting for the first step…</li>}
            </ol>
          </section>

          {runs.length > 1 && (
            <section className="card" style={{ marginTop: 16 }}>
              <h2>Earlier scans</h2>
              <div className="list">
                {runs.map((r) => (
                  <button key={r.id} className={`record ${r.id === selected ? "active" : ""}`} style={{ textAlign: "left", cursor: "pointer", background: "none" }} onClick={() => setSelected(r.id)}>
                    <div className="record-top"><strong>{r.programme_name || "Scan"}</strong><span className="badge">{r.status}</span></div>
                    <span className="meta">{new Date(r.started_at).toLocaleString("en-GB")} · {r.findings_total} findings</span>
                  </button>
                ))}
              </div>
            </section>
          )}
        </>
      )}

      <style>{`
        .steps { list-style: none; margin: 12px 0 0; padding: 0; }
        .step { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid #eceeed; }
        .step:last-child { border-bottom: 0; }
        .step-mark { flex: 0 0 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; background: #eef1f0; color: #2d7d54; }
        .step.active .step-mark { background: #fff4e5; }
        .step.warn .step-mark { background: #fdecea; color: #c0392b; }
        .step.active strong { color: #b26a00; }
        .pulse { width: 9px; height: 9px; border-radius: 50%; background: #e67e22; box-shadow: 0 0 0 0 rgba(230,126,34,.6); animation: pulse 1.3s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(230,126,34,.6);} 70% { box-shadow: 0 0 0 8px rgba(230,126,34,0);} 100% { box-shadow: 0 0 0 0 rgba(230,126,34,0);} }
        .record.active { outline: 2px solid #2d7d54; }
      `}</style>
    </>
  );
}

function Count({ label, value, tone }: { label: string; value: number; tone: string }) {
  return <div className="card" style={{ padding: 12 }}><div className="metric-label">{label}</div><div className="metric-value" style={{ color: tone }}>{value}</div></div>;
}
