"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

const text = (form: FormData, key: string) => String(form.get(key) || "").trim();
const optional = (form: FormData, key: string) => text(form, key) || null;

async function context() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");
  return { supabase, user };
}

async function log(eventType: string, entityType: string, entityId: string | null, description: string) {
  const { supabase, user } = await context();
  await supabase.from("activity_history").insert({ user_id: user.id, event_type: eventType, entity_type: entityType, entity_id: entityId, description });
}

function refresh(...paths: string[]) { paths.forEach((path) => revalidatePath(path)); }

export async function createProgramme(form: FormData) {
  const { supabase, user } = await context();
  const name = text(form, "name");
  if (!name || !text(form, "programme_ref")) return;
  const { data, error } = await supabase.from("programmes").insert({
    user_id: user.id, name, platform: text(form, "platform"), programme_ref: text(form, "programme_ref"),
    enabled: form.get("enabled") === "on", notes: text(form, "notes"), scope_summary: text(form, "scope_summary"), review_due_date: optional(form, "review_due_date"),
  }).select("id").single();
  if (error) throw new Error(error.message);
  await log("programme_created", "programme", data.id, `Programme created: ${name}`);
  refresh("/programmes", "/dashboard", "/brief");
}

export async function updateProgramme(form: FormData) {
  const { supabase } = await context();
  const id = text(form, "id"); const name = text(form, "name");
  const { error } = await supabase.from("programmes").update({ name, platform: text(form, "platform"), programme_ref: text(form, "programme_ref"), enabled: form.get("enabled") === "on", notes: text(form, "notes"), scope_summary: text(form, "scope_summary"), review_due_date: optional(form, "review_due_date") }).eq("id", id);
  if (error) throw new Error(error.message);
  await log("programme_updated", "programme", id, `Programme updated: ${name}`);
  refresh("/programmes", "/dashboard", "/brief");
}

export async function deleteProgramme(form: FormData) {
  const { supabase } = await context(); const id = text(form, "id");
  const { error } = await supabase.from("programmes").delete().eq("id", id);
  if (error) throw new Error(error.message);
  await log("programme_deleted", "programme", id, "Programme deleted"); refresh("/programmes", "/dashboard");
}

export async function createAsset(form: FormData) {
  const { supabase, user } = await context(); const value = text(form, "value"); const programmeId = text(form, "programme_id");
  if (!value || !programmeId) return;
  const { data, error } = await supabase.from("assets").insert({ user_id: user.id, programme_id: programmeId, value, asset_type: text(form, "asset_type"), notes: text(form, "notes") }).select("id").single();
  if (error) throw new Error(error.message);
  await log("asset_created", "asset", data.id, `Asset added: ${value}`); refresh("/programmes", "/findings", "/dashboard");
}

export async function deleteAsset(form: FormData) {
  const { supabase } = await context(); const id = text(form, "id");
  const { error } = await supabase.from("assets").delete().eq("id", id); if (error) throw new Error(error.message);
  await log("asset_deleted", "asset", id, "Asset removed"); refresh("/programmes", "/findings");
}

export async function createFinding(form: FormData) {
  const { supabase, user } = await context(); const title = text(form, "title");
  if (!title || !text(form, "programme_id")) return;
  const { data, error } = await supabase.from("findings").insert({ user_id: user.id, title, description: text(form, "description"), programme_id: text(form, "programme_id"), asset_id: optional(form, "asset_id"), severity: text(form, "severity"), status: text(form, "status"), notes: text(form, "notes"), source_reference: text(form, "source_reference") }).select("id").single();
  if (error) throw new Error(error.message);
  await log("finding_created", "finding", data.id, `Finding created: ${title}`); refresh("/findings", "/dashboard", "/brief", "/analysis", "/search");
}

export async function updateFinding(form: FormData) {
  const { supabase } = await context(); const id = text(form, "id"); const title = text(form, "title");
  const { error } = await supabase.from("findings").update({ title, description: text(form, "description"), programme_id: text(form, "programme_id"), asset_id: optional(form, "asset_id"), severity: text(form, "severity"), status: text(form, "status"), notes: text(form, "notes"), source_reference: text(form, "source_reference") }).eq("id", id);
  if (error) throw new Error(error.message);
  await log("finding_updated", "finding", id, `Finding updated: ${title}`); refresh("/findings", "/dashboard", "/brief", "/analysis", "/search");
}

export async function deleteFinding(form: FormData) {
  const { supabase } = await context(); const id = text(form, "id");
  const { error } = await supabase.from("findings").delete().eq("id", id); if (error) throw new Error(error.message);
  await log("finding_deleted", "finding", id, "Finding deleted"); refresh("/findings", "/dashboard", "/brief", "/analysis");
}

export async function createEvidence(form: FormData) {
  const { supabase, user } = await context(); const findingId = text(form, "finding_id");
  const { data, error } = await supabase.from("evidence").insert({ user_id: user.id, finding_id: findingId, notes: text(form, "notes"), url: text(form, "url"), screenshot_metadata: text(form, "screenshot_metadata"), request_metadata: text(form, "request_metadata"), response_metadata: text(form, "response_metadata"), captured_at: optional(form, "captured_at") || new Date().toISOString() }).select("id").single();
  if (error) throw new Error(error.message);
  await log("evidence_added", "evidence", data.id, "Evidence added"); refresh("/evidence", "/analysis", "/reports", "/brief");
}

export async function deleteEvidence(form: FormData) {
  const { supabase } = await context(); const id = text(form, "id");
  const { error } = await supabase.from("evidence").delete().eq("id", id); if (error) throw new Error(error.message);
  await log("evidence_deleted", "evidence", id, "Evidence deleted"); refresh("/evidence", "/analysis", "/reports");
}

const IMPACT_BY_SEVERITY: Record<string, string> = {
  critical: "This is a critical-severity issue. An attacker could use it to fully compromise the affected system or access highly sensitive data, so it should be reported and fixed as a priority.",
  high: "This is a high-severity issue. An attacker could use the exposed information or weakness to access sensitive data or move further into the system, which is well worth reporting.",
  medium: "This is a medium-severity issue. It gives an attacker useful information or limited access that can support a larger attack, so it should be addressed.",
  low: "This is a low-severity issue. The direct impact is limited, but it still widens the attack surface and is worth tidying up.",
  informational: "This is informational. It is not a vulnerability on its own, but it is useful context that can support a stronger finding.",
};

// Draft a full, submission-ready report from the finding and its evidence.
function buildReportDraft(finding: { title?: string; description?: string; notes?: string; severity?: string } | null,
                          evidence: { notes?: string; url?: string; screenshot_metadata?: string }[]) {
  const severity = (finding?.severity || "medium").toLowerCase();
  // Recover the URL the scanner flagged, from the evidence caption or the finding description.
  let target = "";
  for (const e of evidence) {
    const m = (e.screenshot_metadata || "").match(/https?:\/\/\S+/);
    if (m) { target = m[0]; break; }
  }
  if (!target) { const m = (finding?.description || "").match(/https?:\/\/\S+/); if (m) target = m[0].replace(/[.)]+$/, ""); }
  const where = target || "the affected URL";

  const summary = (finding?.description || finding?.title || "").split("\n")[0]
    || "A security issue was identified on an in-scope asset.";
  const steps = [
    `1. Open the following URL in a normal browser (a simple GET request, no special tools needed):`,
    `   ${where}`,
    `2. Observe that the response is returned publicly, without any login or authorisation.`,
    `3. The attached screenshot shows exactly what the server returned.`,
  ].join("\n");
  const expected = `Requesting ${where} should not expose sensitive information. It should require authentication or return a 403 Forbidden / 404 Not Found response.`;
  const actual = `${where} is publicly accessible and returns sensitive information with no authentication required, as shown in the evidence.`;
  const impact = IMPACT_BY_SEVERITY[severity] || IMPACT_BY_SEVERITY.medium;
  const remediation = `Remove the exposed resource from public access, or require authentication for it. After fixing, re-request ${where} and confirm it no longer returns sensitive data (expect a 403 or 404).`;
  return { summary, steps, expected, actual, impact, remediation };
}

export async function createReport(form: FormData) {
  const { supabase, user } = await context(); const findingId = text(form, "finding_id");
  const { data: finding } = await supabase.from("findings").select("*").eq("id", findingId).single();
  const { data: evidence } = await supabase.from("evidence").select("notes,url,screenshot_metadata").eq("finding_id", findingId);
  const evidenceText = (evidence || []).map((item, index) => `${index + 1}. ${item.screenshot_metadata || item.notes || "Evidence item"}${item.url ? `\n   ${item.url}` : ""}`).join("\n") || "See the evidence attached to this finding.";
  const draft = buildReportDraft(finding, evidence || []);
  const { data, error } = await supabase.from("reports").insert({ user_id: user.id, finding_id: findingId, title: finding?.title || "Finding report", summary: draft.summary, steps: draft.steps, expected_behaviour: draft.expected, actual_behaviour: draft.actual, impact: draft.impact, evidence_text: evidenceText, suggested_remediation: draft.remediation, status: "Draft" }).select("id").single();
  if (error) throw new Error(error.message);
  await log("report_generated", "report", data.id, `Report generated: ${finding?.title || "Finding"}`); refresh("/reports", "/dashboard", "/brief");
}

export async function updateReport(form: FormData) {
  const { supabase } = await context(); const id = text(form, "id"); const title = text(form, "title");
  const { error } = await supabase.from("reports").update({ title, summary: text(form, "summary"), steps: text(form, "steps"), expected_behaviour: text(form, "expected_behaviour"), actual_behaviour: text(form, "actual_behaviour"), impact: text(form, "impact"), evidence_text: text(form, "evidence_text"), suggested_remediation: text(form, "suggested_remediation"), status: text(form, "status") }).eq("id", id);
  if (error) throw new Error(error.message);
  await log("report_updated", "report", id, `Report updated: ${title}`); refresh("/reports", "/dashboard", "/brief");
}

export async function deleteReport(form: FormData) {
  const { supabase } = await context(); const id = text(form, "id");
  const { error } = await supabase.from("reports").delete().eq("id", id); if (error) throw new Error(error.message);
  await log("report_deleted", "report", id, "Report deleted"); refresh("/reports", "/dashboard", "/brief");
}

export async function saveSettings(form: FormData) {
  const { supabase, user } = await context();
  const settings = [
    ["theme", text(form, "theme"), "appearance"], ["evidence_directory", text(form, "evidence_directory"), "directories"],
    ["reports_directory", text(form, "reports_directory"), "directories"], ["future_integrations", text(form, "future_integrations"), "integrations"],
  ].map(([key, value, category]) => ({ user_id: user.id, key, value, category }));
  const { error } = await supabase.from("settings").upsert(settings, { onConflict: "user_id,key" }); if (error) throw new Error(error.message);
  await log("settings_updated", "settings", null, "Workspace settings updated"); refresh("/settings");
}
