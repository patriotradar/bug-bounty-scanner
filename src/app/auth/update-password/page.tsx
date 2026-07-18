import { updatePassword } from "@/lib/auth-actions";

export default async function UpdatePassword({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  const { error } = await searchParams;
  return <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 16 }}><section className="card" style={{ width: "100%", maxWidth: 440 }}>
    <h1>Choose a new password</h1>{error && <p className="notice warning">{error}</p>}
    <form action={updatePassword} className="stack"><div className="field"><label htmlFor="password">New password</label><input id="password" name="password" type="password" minLength={10} required /></div><button className="button">Update password</button></form>
  </section></main>;
}
