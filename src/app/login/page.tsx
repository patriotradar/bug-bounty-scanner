import { login, resetPassword, signup } from "@/lib/auth-actions";

const tutorialSteps = [
  {
    icon: "▣",
    title: "1. Add a programme",
    body: "Go to Programmes → New programme. Enter the scope (domains, IPs, or app names) and the bug bounty platform link. Enable the programme when you're ready to start.",
  },
  {
    icon: "⌕",
    title: "2. Log a finding",
    body: "Open Findings → New finding. Fill in the title, severity (Critical → Informational), affected asset, and a clear reproduction step. Attach screenshots or HTTP logs as evidence.",
  },
  {
    icon: "⌁",
    title: "3. Upload evidence",
    body: "Head to Evidence and upload screenshots, request/response dumps, or PoC videos. Link each file to the relevant finding so your report is fully documented.",
  },
  {
    icon: "▤",
    title: "4. Generate a report",
    body: "Visit Reports → New report. Select the programme and findings you want to include. Preview the draft, then mark it Ready when it's polished and ready to submit.",
  },
  {
    icon: "✦",
    title: "5. Review the analysis",
    body: "The Analysis page surfaces findings that still need attention — unverified, in-progress, or missing evidence. Use it as a daily checklist to stay on top of open work.",
  },
  {
    icon: "☀",
    title: "6. Check your daily brief",
    body: "The Daily Brief gives you a prioritised summary of outstanding findings and upcoming deadlines each morning so you always know where to focus first.",
  },
];

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ error?: string; message?: string }> }) {
  const params = await searchParams;
  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 16 }}>
      <div style={{ width: "100%", maxWidth: 470 }}>
        <section className="card">
          <div className="brand" style={{ color: "#174f48", marginBottom: 20 }}><span className="brand-mark">S</span>ScopeGuard AI</div>
          <h1>Authorised research workspace</h1>
          <p className="meta">Sign in to manage your private programmes, evidence and reports.</p>
          {params.error && <p className="notice warning">{params.error}</p>}
          {params.message && <p className="notice">{params.message}</p>}
          <form className="stack" style={{ marginTop: 20 }}>
            <div className="field"><label htmlFor="email">Email</label><input id="email" name="email" type="email" required autoComplete="email" /></div>
            <div className="field"><label htmlFor="password">Password</label><input id="password" name="password" type="password" minLength={10} required autoComplete="current-password" /></div>
            <div className="actions">
              <button className="button" formAction={login}>Sign in</button>
              <button className="button secondary" formAction={signup}>Create account</button>
              <button className="button secondary" formAction={resetPassword}>Reset password</button>
            </div>
          </form>
          <p className="meta" style={{ marginTop: 20 }}>ScopeGuard organises human-led, explicitly authorised research. It does not perform scans or exploitation.</p>
        </section>

        <details className="tutorial-panel">
          <summary className="tutorial-summary">
            <span className="tutorial-summary-icon">?</span>
            How to use ScopeGuard AI
            <span className="tutorial-caret" aria-hidden>▾</span>
          </summary>
          <div className="tutorial-body">
            <p className="tutorial-intro">New here? Follow these six steps to go from zero to a polished bug-bounty report.</p>
            <ol className="tutorial-steps">
              {tutorialSteps.map((step) => (
                <li key={step.title} className="tutorial-step">
                  <span className="tutorial-step-icon" aria-hidden>{step.icon}</span>
                  <div>
                    <strong className="tutorial-step-title">{step.title}</strong>
                    <p className="tutorial-step-body">{step.body}</p>
                  </div>
                </li>
              ))}
            </ol>
            <p className="meta" style={{ marginTop: 16 }}>
              All research must be explicitly authorised. ScopeGuard never performs automated scanning or exploitation.
            </p>
          </div>
        </details>
      </div>
    </main>
  );
}
