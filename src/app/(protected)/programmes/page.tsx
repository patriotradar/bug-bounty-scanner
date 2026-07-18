import { Badge, Empty, PageHead } from "@/components/app-shell";
import { createAsset, createProgramme, deleteAsset, deleteProgramme, updateProgramme } from "@/lib/actions";
import { createClient } from "@/lib/supabase/server";
import { assetTypes, type Asset, type Programme } from "@/lib/types";

export default async function ProgrammesPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q = "" } = await searchParams; const supabase = await createClient();
  let query = supabase.from("programmes").select("*").order("enabled", { ascending: false }).order("name");
  if (q) query = query.or(`name.ilike.%${q}%,platform.ilike.%${q}%,programme_ref.ilike.%${q}%`);
  const { data } = await query; const programmes = (data || []) as Programme[];
  const { data: assetData } = await supabase.from("assets").select("*").order("value"); const assets = (assetData || []) as Asset[];
  return <><PageHead title="Programmes" description="Manage authorised programmes and exact scope assets" />
    <section className="card"><h2>Create programme</h2><ProgrammeForm action={createProgramme}/></section>
    <form className="card" style={{ marginTop: 16 }}><div className="field"><label htmlFor="q">Search programmes</label><div className="actions"><input id="q" name="q" defaultValue={q}/><button className="button">Search</button></div></div></form>
    <div className="stack" style={{ marginTop: 16 }}>{programmes.map(programme=><article className="card" id={programme.id} key={programme.id}>
      <div className="record-top"><div><h2>{programme.name}</h2><div className="meta">{programme.platform || "Platform not recorded"} · {programme.programme_ref}</div></div><Badge>{programme.enabled ? "Enabled" : "Disabled"}</Badge></div>
      <details><summary>Edit programme</summary><ProgrammeForm programme={programme} action={updateProgramme}/></details>
      <h3 style={{ marginTop: 22 }}>In-scope assets</h3><div className="list">{assets.filter(a=>a.programme_id===programme.id).map(asset=><div className="record" key={asset.id}><div className="record-top"><div><strong>{asset.value}</strong><div className="meta">{asset.asset_type} · {asset.notes}</div></div><form action={deleteAsset}><input type="hidden" name="id" value={asset.id}/><button className="button danger">Remove</button></form></div></div>)}{!assets.some(a=>a.programme_id===programme.id)&&<div className="notice warning">No assets recorded. Research should remain blocked until exact scope is added.</div>}</div>
      <form action={createAsset} className="form-grid" style={{marginTop:14}}><input type="hidden" name="programme_id" value={programme.id}/><div className="field"><label>Asset value</label><input name="value" required/></div><div className="field"><label>Type</label><select name="asset_type">{assetTypes.map(type=><option key={type}>{type}</option>)}</select></div><div className="field full"><label>Notes</label><input name="notes"/></div><button className="button">Add asset</button></form>
      <form action={deleteProgramme} style={{marginTop:16}}><input type="hidden" name="id" value={programme.id}/><button className="button danger">Delete programme</button></form>
    </article>)}{!programmes.length&&<Empty>No programmes match your search.</Empty>}</div>
  </>;
}

function ProgrammeForm({ programme, action }: { programme?: Programme; action: (form: FormData)=>Promise<void> }) { return <form action={action} className="form-grid">
  {programme&&<input type="hidden" name="id" value={programme.id}/>}<div className="field"><label>Name</label><input name="name" defaultValue={programme?.name} required/></div><div className="field"><label>Platform</label><input name="platform" defaultValue={programme?.platform}/></div><div className="field"><label>Programme ID</label><input name="programme_ref" defaultValue={programme?.programme_ref} required/></div><div className="field"><label>Review due</label><input name="review_due_date" type="date" defaultValue={programme?.review_due_date || ""}/></div><div className="field full"><label>Scope summary</label><textarea name="scope_summary" defaultValue={programme?.scope_summary}/></div><div className="field full"><label>Notes</label><textarea name="notes" defaultValue={programme?.notes}/></div><label><input name="enabled" type="checkbox" defaultChecked={programme?.enabled ?? true} style={{width:18,minHeight:18}}/> Enabled</label><button className="button">{programme ? "Save programme" : "Create programme"}</button>
  </form>; }
