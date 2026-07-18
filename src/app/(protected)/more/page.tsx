import Link from "next/link";
import { PageHead } from "@/components/app-shell";

const links = [["Daily brief","/brief"],["Evidence","/evidence"],["Reports","/reports"],["Analysis","/analysis"],["Global search","/search"],["Settings","/settings"]];
export default function MorePage() { return <><PageHead title="More" description="All ScopeGuard tools"/><div className="grid two">{links.map(([label,href])=><Link className="card" href={href} key={href}><h2>{label}</h2><span className="meta">Open →</span></Link>)}</div></>; }
