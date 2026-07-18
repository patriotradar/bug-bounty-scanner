import Link from "next/link";
import { logout } from "@/lib/auth-actions";

const navigation = [
  ["Dashboard", "/dashboard", "⌂"], ["Daily brief", "/brief", "☀"],
  ["Programmes", "/programmes", "▣"], ["Findings", "/findings", "⌕"],
  ["Evidence", "/evidence", "⌁"], ["Reports", "/reports", "▤"],
  ["Analysis", "/analysis", "✦"], ["Search", "/search", "⌕"],
  ["Settings", "/settings", "⚙"],
];

export function AppShell({ children, email }: { children: React.ReactNode; email?: string }) {
  return <div className="shell">
    <header className="topbar">
      <Link className="brand" href="/dashboard"><span className="brand-mark">S</span>ScopeGuard AI</Link>
      <form action={logout}><button className="button secondary" type="submit">Sign out</button></form>
    </header>
    <div className="layout">
      <aside className="sidebar">
        <nav className="nav">{navigation.map(([label, href, icon]) => <Link href={href} key={href}><span aria-hidden>{icon}</span> {label}</Link>)}</nav>
        {email && <p className="meta" style={{ margin: "24px 12px" }}>Signed in as<br />{email}</p>}
      </aside>
      <main className="content">{children}<div className="footer-space" /></main>
    </div>
    <nav className="mobile-nav" aria-label="Mobile navigation">
      {navigation.slice(0, 4).map(([label, href, icon]) => <Link href={href} key={href}><span>{icon}</span>{label}</Link>)}
      <Link href="/more"><span>•••</span>More</Link>
    </nav>
  </div>;
}

export function PageHead({ title, description }: { title: string; description: string }) {
  return <div className="page-head"><div><h1>{title}</h1><p>{description}</p></div><div className="safety">Human-controlled research only</div></div>;
}

export function Empty({ children }: { children: React.ReactNode }) { return <div className="empty">{children}</div>; }
export function Badge({ children }: { children: React.ReactNode }) {
  const slug = String(children).toLowerCase().replaceAll(" ", "-");
  return <span className={`badge ${slug}`}>{children}</span>;
}
