import { login, resetPassword, signup } from "@/lib/auth-actions";

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ error?: string; message?: string }> }) {
  const params = await searchParams;
  return <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 16 }}>
    <section className="card" style={{ width: "100%", maxWidth: 470 }}>
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
  </main>;
}
