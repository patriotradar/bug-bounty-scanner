import Link from "next/link";
import { Badge, Empty, PageHead } from "@/components/app-shell";
import { createClient } from "@/lib/supabase/server";

export default async function Dashboard() {
  const supabase = await createClient();
  const [programmes, findings, reports, activity] = await Promise.all([
    supabase.from("programmes").select("id,name,enabled"),
    supabase.from("findings").select("id,title,severity,status"),
    supabase.from("reports").select("id,status"),
    supabase.from("activity_history").select("id,description,created_at").order("created_at", { ascending: false }).limit(8),
  ]);
  const programmeRows = programmes.data || []; const findingRows = findings.data || []; const reportRows = reports.data || [];
  const severity = ["Critical","High","Medium","Low","Informational"].map(name => ({ name, count: findingRows.filter(f => f.severity === name).length }));
  const max = Math.max(1, ...severity.map(item => item.count));
  return <><PageHead title="Dashboard" description="Your authorised research workspace at a glance" />
    <div className="grid metrics">
      <Metric label="Active programmes" value={programmeRows.filter(p=>p.enabled).length}/><Metric label="All programmes" value={programmeRows.length}/>
      <Metric label="Findings" value={findingRows.length}/><Metric label="Pending reports" value={reportRows.filter(r=>["Draft","Ready"].includes(r.status)).length}/>
    </div>
    <div className="grid two" style={{ marginTop: 16 }}>
      <section className="card"><h2>Severity breakdown</h2>{severity.map(item=><div className="bar-row" key={item.name}><span>{item.name}</span><span className="bar"><span style={{width:`${(item.count/max)*100}%`}}/></span><strong>{item.count}</strong></div>)}</section>
      <section className="card"><div className="record-top"><h2>Work needing attention</h2><Link className="button secondary" href="/analysis">Open analysis</Link></div>
        <div className="list">{findingRows.filter(f=>!["Submitted","Closed"].includes(f.status)).slice(0,6).map(f=><Link className="record" href={`/findings#${f.id}`} key={f.id}><div className="record-top"><h3>{f.title}</h3><Badge>{f.severity}</Badge></div><span className="meta">{f.status}</span></Link>)}{!findingRows.length&&<Empty>No findings yet.</Empty>}</div>
      </section>
    </div>
    <section className="card" style={{ marginTop: 16 }}><h2>Recent activity</h2><div className="list">{(activity.data||[]).map(item=><div className="record" key={item.id}><strong>{item.description}</strong><div className="meta">{new Date(item.created_at).toLocaleString("en-GB")}</div></div>)}{!activity.data?.length&&<Empty>Your activity history will appear here.</Empty>}</div></section>
  </>;
}

function Metric({label,value}:{label:string;value:number}) { return <div className="card"><div className="metric-label">{label}</div><div className="metric-value">{value}</div></div>; }
