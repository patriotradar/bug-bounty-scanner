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

export async function createKnownIssue(form: FormData) {
  const { supabase, user } = await context();
  const programmeId = text(form, "programme_id"); const pattern = text(form, "pattern");
  if (!programmeId || !pattern) return;
  const matchType = text(form, "match_type") === "template" ? "template" : "keyword";
  const { data, error } = await supabase.from("known_issues").insert({
    user_id: user.id, programme_id: programmeId, match_type: matchType, pattern, note: text(form, "note"),
  }).select("id").single();
  if (error) throw new Error(error.message);
  await log("known_issue_created", "known_issue", data.id, `Known issue added (${matchType}): ${pattern}`);
  refresh("/programmes");
}

export async function deleteKnownIssue(form: FormData) {
  const { supabase } = await context(); const id = text(form, "id");
  const { error } = await supabase.from("known_issues").delete().eq("id", id);
  if (error) throw new Error(error.message);
  await log("known_issue_deleted", "known_issue", id, "Known issue removed"); refresh("/programmes");
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

type EvidenceRow = { notes?: string; url?: string; screenshot_metadata?: string; request_metadata?: string; response_metadata?: string };
type FindingRow = { title?: string; description?: string; notes?: string; severity?: string; confidence?: string; verification_status?: string };

// Pull a labelled section (written by capture_evidence.py) out of an evidence note.
function section(notes: string, label: string): string {
  const re = new RegExp(`${label}:\\n([\\s\\S]*?)(?:\\n\\n[A-Z][A-Z ]+:\\n|$)`);
  const m = notes.match(re);
  return m ? m[1].trim() : "";
}

// Impact described ONLY from what the evidence proves - no generic "attacker could fully compromise".
function evidenceImpact(severity: string, observed: string, where: string): string {
  const sev = (severity || "").toLowerCase();
  const hasSecret = /credential|private key|token|password|secret|api key|connection string/i.test(observed);
  if (hasSecret && (sev === "high" || sev === "critical")) {
    return `The response at ${where} is publicly reachable and contains the sensitive values listed under Observed Data. `
      + `If those values are valid in production, anyone who requests this URL could reuse them to authenticate or access `
      + `back-end services. The impact is bounded by what the exposed material actually unlocks, which the researcher should `
      + `confirm before submission - this report does not assume more than the evidence shows.`;
  }
  if (hasSecret) {
    return `The response at ${where} exposes token/secret-shaped values (see Observed Data). Their real impact depends on `
      + `whether they are live and what they grant; this has not been proven here, so the impact is stated conservatively as `
      + `potential credential exposure pending verification.`;
  }
  if (/internal hostname|private ip|feature flag|internal settings/i.test(observed)) {
    return `The response at ${where} discloses internal configuration (hostnames, settings) that aids reconnaissance. `
      + `No credentials or sensitive data were demonstrated, so the direct impact is limited to information disclosure.`;
  }
  return `The file at ${where} is publicly reachable, but the captured response contains only non-sensitive/public `
    + `configuration. No sensitive data or exploitable behaviour was demonstrated, so the practical impact is limited. `
    + `Reported for completeness; confirm before submitting.`;
}

// Remediation tailored to what was actually observed.
function remediationFor(observed: string, where: string): string {
  const steps: string[] = [];
  if (/private key|credential|password|connection string|secret|api key|token/i.test(observed)) {
    steps.push("Rotate any credentials, keys or tokens that were exposed - treat them as compromised.");
    steps.push("Remove the secrets from any client-side or publicly served file and move configuration server-side.");
  }
  steps.push(`Restrict public access to ${where} - require authentication or return a 403/404 for it.`);
  steps.push(`After fixing, re-request ${where} and confirm it no longer returns the data shown in the evidence.`);
  return steps.map((s, i) => `${i + 1}. ${s}`).join("\n");
}

// Build a submission-ready, evidence-driven report from the finding and its collected evidence.
function buildReportDraft(finding: FindingRow | null, evidence: EvidenceRow[]) {
  const auto = evidence.find((e) => (e.screenshot_metadata || "").startsWith("Auto-captured")) || evidence[0] || {};
  const notes = auto.notes || "";
  let where = "";
  const wm = (auto.screenshot_metadata || "").match(/https?:\/\/\S+/);
  if (wm) where = wm[0];
  if (!where && auto.request_metadata) { const m = auto.request_metadata.match(/https?:\/\/\S+/); if (m) where = m[0]; }
  if (!where) { const m = (finding?.description || "").match(/https?:\/\/\S+/); if (m) where = m[0].replace(/[.)]+$/, ""); }
  where = where || "the affected URL";

  const observed = section(notes, "OBSERVED DATA") || "Not recorded - re-run evidence collection for this finding.";
  const justification = section(notes, "SEVERITY JUSTIFICATION")
    || "Severity should be set from the evidence; re-run evidence collection to populate this.";
  const confidenceBlock = section(notes, "CONFIDENCE");
  const confidence = (finding?.confidence || confidenceBlock.split(" - ")[0] || "Low").trim();
  const confidenceReason = confidenceBlock.includes(" - ") ? confidenceBlock.split(" - ").slice(1).join(" - ") : confidenceBlock;
  const verification = finding?.verification_status || section(notes, "VERIFICATION STATUS") || "Needs manual review";
  const redactedBody = section(notes, "REDACTED RESPONSE BODY");
  const severity = finding?.severity || "Informational";

  const summary = `A publicly accessible resource was found at ${where}. `
    + `This report is built only from what was actually returned by the server (see Evidence). `
    + `Severity is estimated from that evidence and the finding is a scanner lead that still needs manual verification.`;

  const steps = [
    "1. Send the following request (a plain GET, no tools or auth required):",
    (auto.request_metadata ? auto.request_metadata.split("\n").map((l) => `   ${l}`).join("\n") : `   GET ${where}`),
    "2. Observe the response returned below - it comes back publicly, with no authentication.",
    "3. The attached screenshot shows exactly what the server returned at capture time.",
  ].join("\n");

  const expected = `Requesting ${where} should not return sensitive or internal information without authorisation. `
    + `It should require authentication or return 403 Forbidden / 404 Not Found.`;
  const respLine = (auto.response_metadata || "").split("\n")[0] || "the response shown in Evidence";
  const actual = `${where} is publicly reachable and returned ${respLine}. The full response and what was observed in it are in the Evidence and Observed Data sections.`;

  const evidenceText = [
    "--- HTTP REQUEST ---",
    auto.request_metadata || `GET ${where}`,
    "",
    "--- HTTP RESPONSE ---",
    auto.response_metadata || "Not recorded - re-run evidence collection.",
    "",
    "--- RESPONSE BODY (secrets redacted) ---",
    redactedBody || "Not recorded.",
    "",
    auto.url ? `--- SCREENSHOT ---\n${auto.url}` : "",
  ].filter(Boolean).join("\n");

  return {
    severity,
    severityJustification: justification,
    confidence: confidenceReason ? `${confidence} - ${confidenceReason}` : confidence,
    verification,
    observed,
    summary,
    steps,
    expected,
    actual,
    impact: evidenceImpact(severity, observed, where),
    evidenceText,
    remediation: remediationFor(observed, where),
  };
}

export async function createReport(form: FormData) {
  const { supabase, user } = await context(); const findingId = text(form, "finding_id");
  const { data: finding } = await supabase.from("findings").select("*").eq("id", findingId).single();
  const { data: evidence } = await supabase.from("evidence").select("notes,url,screenshot_metadata,request_metadata,response_metadata").eq("finding_id", findingId);
  const draft = buildReportDraft(finding, (evidence || []) as EvidenceRow[]);
  const { data, error } = await supabase.from("reports").insert({
    user_id: user.id, finding_id: findingId, title: finding?.title || "Finding report",
    summary: draft.summary, steps: draft.steps, expected_behaviour: draft.expected, actual_behaviour: draft.actual,
    impact: draft.impact, evidence_text: draft.evidenceText, suggested_remediation: draft.remediation,
    severity: draft.severity, severity_justification: draft.severityJustification, observed_data: draft.observed,
    confidence: draft.confidence, verification_status: draft.verification, status: "Draft",
  }).select("id").single();
  if (error) throw new Error(error.message);
  await log("report_generated", "report", data.id, `Report generated: ${finding?.title || "Finding"}`); refresh("/reports", "/dashboard", "/brief");
}

export async function updateReport(form: FormData) {
  const { supabase } = await context(); const id = text(form, "id"); const title = text(form, "title");
  const { error } = await supabase.from("reports").update({ title, summary: text(form, "summary"), severity: text(form, "severity"), severity_justification: text(form, "severity_justification"), confidence: text(form, "confidence"), verification_status: text(form, "verification_status"), observed_data: text(form, "observed_data"), steps: text(form, "steps"), expected_behaviour: text(form, "expected_behaviour"), actual_behaviour: text(form, "actual_behaviour"), impact: text(form, "impact"), evidence_text: text(form, "evidence_text"), suggested_remediation: text(form, "suggested_remediation"), status: text(form, "status") }).eq("id", id);
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
